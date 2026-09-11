"""Capture report evidence without importing the experiment or reading sealed items.

Run from any directory with Python 3. The destination must be new. CPU only.
"""

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = [
    'manifests/frozen.json', 'results/REG/epc-50m/summary.json',
    'results/REG/preflight.json', 'results/S1/P1_epc.json',
    'results/S1/P2_epc.json', 'results/S1/P3_epc.json',
    'results/S1/P4_gram.json', 'results/S1/P6_epc.json',
    'results/S2/throughput_v2.json', 'results/S2/throughput_v2_baselines.json',
    'results/S2/projection.json', 'results/S5/projection.json',
    'results/S3/grammar_dev_matrix.json', 'results/S3/fixture/summary.json',
    'results/S3/cr_reprofile.json', 'manifests/cr_distribution.json',
    'results/S2/grace_jax/pc10.json', 'results/S2/grace_jax/sensitivity.json',
    'results/S2/grace_jax/gradient_localization/candidate.json',
    'results/S2/grace_jax/gradient_localization/head_loss_probes.json',
    'results/S2/grace_jax/gradient_localization/reduction_replay_candidate.json',
    'results/S3/control_audit_round4/run.json', 'results/ENV/kappa.json',
    'logs/reproduce_round4/summary.json', 'logs/reproduce_round4/followup.json',
    'results/S4/jobs.json', 'results/S4/queue.jsonl',
    'docs/ongoing.md', 'docs/updated_plan8.md', 'docs/decisions.md',
    'docs/spec_defects.md', 'docs/controls.md', 'docs/REPRODUCE.md',
    'docs/environment.md', 'docs/pdf_text/plan.txt',
    'logs/review_p4_s7_r2.md', 'logs/grace_gradient_localization.md',
    'logs/reproduce_preaudit.md', 'src/pccap/harness/stage_s4.py',
    'src/pccap/harness/stage_s5.py', 'src/pccap/harness/runs.py',
    'src/pccap/harness/stage_s3.py', 'src/pccap/analysis/bootstrap.py',
    'src/pccap/analysis/paired.py', 'scripts/s4_progress.py',
]


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def capture():
    out = {'capture_started_utc': stamp(), 'sources': {}, 'runs': []}
    out['git_head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out['git_status_before'] = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)

    def add(path, raw=None):
        raw = (ROOT / path).read_bytes() if raw is None else raw
        out['sources'][path] = {
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
            'content': json.loads(raw) if path.endswith('.json') else raw.decode(),
        }
        return out['sources'][path]['content']

    for path in SOURCES:
        add(path)
    historical = 'git:25c988b:results/S1/P1_epc.json'
    add(historical, subprocess.check_output(['git', 'show', '25c988b:results/S1/P1_epc.json'], cwd=ROOT))
    pdf = ROOT / 'docs/pc_cap_month_plan_readable.pdf'
    out['plan_pdf_sha256'] = hashlib.sha256(pdf.read_bytes()).hexdigest()
    frozen = out['sources']['manifests/frozen.json']
    out['frozen_sha256'] = frozen['sha256']
    out['experiment_id'] = frozen['content']['name'] + '-' + frozen['sha256'][:8]
    out['progress'] = json.loads(subprocess.check_output(['python3', 'scripts/s4_progress.py', '--json'], cwd=ROOT))
    queue_text = out['sources']['results/S4/queue.jsonl']['content']
    attempts = [json.loads(line) for line in queue_text.splitlines() if line.strip()]
    for a in attempts:
        if a.get('status') != 'complete':
            continue
        j = a['job']
        run = ROOT / 'results/S4' / out['experiment_id'] / j['dataset'] / j['arm'] / j.get('base', 'BP') / j.get('read', 'h') / str(j['realization']) / str(j['perm'])
        cfg = json.loads((run / 'config.json').read_bytes())
        if cfg.get('status') != 'complete' or cfg.get('experiment_id') != out['experiment_id']:
            continue
        assert cfg['frozen_manifest_sha256'] == out['frozen_sha256']
        assert cfg['base_hash_before'] == cfg['base_hash_after']
        add(str((run / 'config.json').relative_to(ROOT)))
        add(str((run / 'metrics.json').relative_to(ROOT)))
        out['runs'].append({'path': str(run.relative_to(ROOT)), 'job': j,
                            'queue_wall_seconds': a['wall_seconds'], 'config': cfg})
    assert len(out['runs']) == out['progress']['finished'], 'Queue changed during snapshot; use a new destination.'
    assert out['plan_pdf_sha256'] == frozen['content']['pdf_sha']
    assert all(len(c['common_input_components']) == 27 for c in out['sources']['results/S2/grace_jax/gradient_localization/candidate.json']['content']['cases'])
    out['capture_finished_utc'] = stamp()
    out['limitations'] = [
        'Read-only snapshot; no new scientific experiments or GPU calls.',
        'Only completed, matching v2 run aggregates captured; sealed item manifests were not opened.',
        'Live queue may advance after this cutoff. Progress ETA is a heuristic, not an uncertainty interval.',
        'Historical full P1 and smaller live P1 remain separate evidence records.',
    ]
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('destination', type=Path)
    args = ap.parse_args()
    if args.destination.exists():
        raise SystemExit('Refusing to overwrite evidence')
    data = capture()
    with args.destination.open('x') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
    print(json.dumps({k: data[k] for k in ['capture_finished_utc', 'git_head', 'experiment_id']}, indent=2))
    print('Completed S4 runs:', len(data['runs']))
