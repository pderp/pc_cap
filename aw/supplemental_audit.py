"""X25: independent saved-byte/receipt audit; no inference or model imports.

Only declared file hashes are checked (parameter-tree hashes are not file hashes).
Historical PC source substitutions must be explicitly allowed by pc_historical.
Partial/failed receipts are listed, never converted to completed experiments.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from aw.pc_historical import ROOT
from aw.reporting_sources import Sources

REPORTS = {
    'PC-v0': 'PC-v0/report-60-20260927/report.json',
    'PC-v0 harm': 'PC-v0/report-60-20260927/harm/report.json',
    'PC-v1': 'PC-v1/report-4-20260927/report.json',
    'PC-v1 harm': 'PC-v1/report-4-20260927/harm/report.json',
    'depth/random controls': 'PC-v0/controls-report-20260929/report.json',
    'matched control': 'PC-v0/matched-report-20261001/report.json',
    'AW-B': 'AW-B/report-20260929/report.json',
    'PC-reader': 'PC-reader/report-round63-final/report.json',
    'Option R': 'R/report-round63-final/report.json',
    'AW-L': 'AW-L/report-round63-final/report.json',
    'HT-17': 'HT-17/snapshot-20261004-complete/report.json',
}
HASH = re.compile(r'^[0-9a-f]{64}$')


def bindings(value):
    """Yield file bindings, not bare scientific/parameter identity fields."""
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and HASH.fullmatch(str(value.get('sha256', ''))):
            yield value['path'], value['sha256']
        for key, item in value.items():
            if (key in ('sources', 'code_sha256') or key.endswith('sources_sha256') or key.endswith('_sources')) and isinstance(item, dict):
                for name, identity in item.items():
                    if isinstance(identity, str) and HASH.fullmatch(identity) and ('/' in name or '.' in name):
                        yield name, identity
            yield from bindings(item)
    elif isinstance(value, list):
        for item in value:
            yield from bindings(item)


class Audit:
    def __init__(self):
        self.cache = {}
        self.historical = Sources()

    def digest(self, path):
        path = Path(path).resolve()
        st = path.stat()
        signature = (st.st_size, st.st_mtime_ns)
        if path not in self.cache or self.cache[path][0] != signature:
            with path.open('rb') as f:
                digest = hashlib.file_digest(f, 'sha256').hexdigest()
            if signature != (path.stat().st_size, path.stat().st_mtime_ns):
                raise ValueError('file changed during hash read')
            self.cache[path] = signature, digest
        return self.cache[path][1]

    def check(self, name, expected):
        path = Path(name)
        path = path if path.is_absolute() else ROOT / path
        try:
            actual = self.digest(path)
            if actual == expected:
                return {'path': str(path), 'expected': expected, 'status': 'PASS'}
            resolved = self.historical.resolve(path, expected)
            return {'path': str(path), 'expected': expected, 'status': 'PASS', 'historical_archive': str(resolved)}
        except (OSError, ValueError) as exc:
            return {'path': str(path), 'expected': expected, 'status': 'FAIL', 'reason': str(exc)}

    def report(self, name, path, extra=()):
        path = Path(path).resolve()
        documents = [path, *map(Path, extra)]
        # First-level cited raw metadata supplies its own nested source bindings.
        declared = set()
        receipts = []
        for doc in list(documents):
            data = json.loads(doc.read_bytes())
            declared.update(bindings(data))
            if 'source_inventory_sha256' in data:
                declared.add((str(doc.parent / 'sources.json'), data['source_inventory_sha256']))
            for source, _ in list(bindings(data)):
                p = Path(source)
                p = p if p.is_absolute() else ROOT / p
                if p.suffix == '.json' and p.is_file() and ('/results/additional_work/' in str(p) or p.name in ('finish.json', 'session-finish.json')):
                    documents.append(p)
        documents = sorted(set(documents))
        for doc in documents:
            data = json.loads(doc.read_bytes())
            declared.update(bindings(data))
            if doc.name == 'finish.json' and 'start_sha256' in data:
                declared.add((str(doc.with_name('start.json')), data['start_sha256']))
            if 'config_sha256' in data and doc.with_name('config.json').exists():
                declared.add((str(doc.with_name('config.json')), data['config_sha256']))
            # Raw, enclosing receipt inventory; costs overlap and are not summed.
            if doc.name in ('finish.json', 'cost.json', 'session-finish.json', 'session-end.json'):
                status = data.get('status', 'ledger-only; completion in finish receipt')
                seconds = data.get('elapsed_process_seconds', data.get('elapsed_wall_seconds', data.get('charged_process_wall_seconds')))
                if 'returncode' in data:
                    status = 'complete' if data['returncode'] == 0 else 'stopped/failed child process'
                errors = []
                if status == 'complete':
                    if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or not math.isfinite(seconds) or seconds < 0:
                        errors.append('complete receipt lacks finite nonnegative process time')
                    if 'items_planned' in data and data.get('items_completed') != data['items_planned']:
                        errors.append('complete receipt has unfinished items')
                    for key in ('base', 'reader'):
                        if f'{key}_hash_before' in data and data[f'{key}_hash_before'] != data.get(f'{key}_hash_after'):
                            errors.append(f'{key} changed')
                receipts.append(dict(path=str(doc), status=status, seconds=seconds, errors=errors, cell_id=data.get('cell_id')))
        checks = [self.check(*entry) for entry in sorted(declared)]
        failures = [r for r in checks if r['status'] == 'FAIL']
        failures += [r for r in receipts if r['errors']]
        independent = {}
        reported = json.loads(path.read_bytes())
        if isinstance(reported, dict) and reported.get('task') == 'R-3':
            attempts = [r for r in receipts if r['cell_id']]
            total = sum(r['seconds'] for r in attempts) if all(isinstance(r['seconds'], (int, float)) for r in attempts) else None
            complete = {r['cell_id'] for r in attempts if r['status'] == 'complete'}
            expected = {r['cell_id'] for r in reported['cells'] if r['artifact_complete']}
            independent = dict(charged_process_seconds=total, successful_cell_ids=sorted(complete),
                               matches_reported_cost=total is not None and math.isclose(total, reported['charged_process_seconds'], abs_tol=1e-7),
                               matches_reported_completion=complete == expected)
            if not independent['matches_reported_cost'] or not independent['matches_reported_completion']:
                failures.append(dict(reason='Option R enclosing costs/completion differ', checks=independent))
        return dict(name=name, independent_checks=independent, source=str(path), source_sha256=self.digest(path),
                    status='FAIL' if failures else 'PASS', bindings=checks, receipts=receipts,
                    discrepancies=failures, metadata_files=[str(p) for p in documents])


def run(output, overrides=None, deck=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    audit = Audit()
    reports = dict(REPORTS)
    reports.update(overrides or {})
    rows = []
    for name, rel in reports.items():
        path = Path(rel)
        path = path if path.is_absolute() else ROOT / 'logs/additional_work' / path
        extra = [path.parent / 'sources.json'] if name == 'HT-17' else []
        rows.append(audit.report(name, path, extra))
    if deck:
        rows.append(audit.report('rehearsal deck', Path(deck) / 'manifest.json', [Path(deck) / 'rehearsal-manifest.json']))
    # Profiles and credit-setting variants have raw receipts, not a synthesized
    # numerical report. Audit them independently of the presentation resolver.
    roots = list((ROOT / 'results/additional_work/PC-v1').glob('replication-4-*'))
    roots += list((ROOT / 'results/additional_work/PC-reader').glob('profile*'))
    roots += list((ROOT / 'results/additional_work/PC-v1').glob('profile*'))
    roots += list((ROOT / 'results/additional_work/PC-v0').glob('dev-profile*'))
    for root in sorted(roots):
        paths = sorted(root.rglob('*.json'))
        if paths:
            rows.append(audit.report(str(root.relative_to(ROOT)), paths[0], paths[1:]))
    record = dict(task='X25', created_utc=datetime.now(timezone.utc).isoformat(),
                  status='FAIL' if any(r['status'] == 'FAIL' for r in rows) else 'PASS',
                  reports=rows, unique_files_hashed=len(audit.cache),
                  scope='Declared file hashes and raw receipts; no model execution, new scoring or inference. Narrative coverage is reviewed separately in review.md.',
                  producer_sha256=audit.digest(__file__), gpu_seconds=0)
    (output / 'audit.json').write_text(json.dumps(record, indent=2) + '\n')
    with (output / 'table.csv').open('w') as f:
        w = csv.writer(f)
        w.writerow(['report', 'status', 'bindings', 'receipts', 'discrepancies'])
        w.writerows((r['name'], r['status'], len(r['bindings']), len(r['receipts']), len(r['discrepancies'])) for r in rows)
    print(json.dumps({k: record[k] for k in ('status', 'unique_files_hashed')}))
    print('\n'.join(f"{r['status']} {r['name']}: {len(r['discrepancies'])}" for r in rows))
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reports', type=Path, help='JSON name:path overrides for later canonical snapshots')
    parser.add_argument('--deck', type=Path, help='canonical rehearsal/deck directory')
    args = parser.parse_args()
    run(args.output, json.loads(args.reports.read_text()) if args.reports else None, args.deck)
