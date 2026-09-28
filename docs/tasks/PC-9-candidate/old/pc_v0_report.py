"""PC-3: verified paired summaries of PC-v0 run groups; never executes a model."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = {'ES': 'es_immediate', 'RET-ES': 'ret_es_end', 'RET-GS': 'ret_gs_end',
           'LS': 'ls_complete_answer_end'}
SECONDARY = ('bounded_es_immediate', 'bounded_ret_es_end', 'bounded_ret_gs_end', 'bounded_ls_end')


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path, bindings):
    value = json.loads(Path(path).read_bytes())
    bindings[str(Path(path).resolve())] = sha(path)
    return value


def verify(path, expected, bindings):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    if bindings.get(str(path)) == expected:
        return
    if sha(path) != expected:
        raise ValueError(f'identity mismatch: {path}')
    bindings[str(path)] = expected


def finite(value):
    if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
        raise ValueError('nonfinite or nonnumeric metric')
    return value


def coordinate(c):
    return c['dataset'], c['realization'], c['order'], c['arm']


def expected_cells(orders):
    return [dict(dataset=d, realization=r, order=o, arm=a, items=1000 if d == 'zsre' else 300)
            for d in ('zsre', 'counterfact') for r in range(3)
            for o in range(100, 100 + orders) for a in ('SE-A', 'SE-E')]


def load_group(path, bindings, *, smoke=False, diagnostic=False):
    path = Path(path)
    plan = read(path / 'plan.json', bindings)
    is_smoke = plan.get('population') == 'cpu_smoke'
    if is_smoke != smoke or (not smoke and plan.get('population') != ('development' if diagnostic else 'exposed S5')):
        raise ValueError('development/smoke/replication populations cannot be mixed')
    if not smoke:
        from aw.pc_v0 import source_identities
        if plan['sources'] != source_identities():
            raise ValueError('runner source inventory differs; review source drift before reporting')
    for name, digest in plan['sources'].items():
        verify(name, digest, bindings)
    rows = []
    for c in plan['cells']:
        ds, r, o, a = coordinate(c)
        dest = path / f'{ds}-r{r}-o{o}-{a}'
        row = dict(c, status='missing', metrics={}, secondary={}, directory=str(dest.resolve()))
        cfg_path, finish_path = dest / 'config.json', dest / 'finish.json'
        if not cfg_path.exists():
            if finish_path.exists():
                finish = read(finish_path, bindings)
                if finish['status'] == 'complete':
                    raise ValueError('complete cell has no configuration')
                row.update(status=finish['status'], finish=finish)
            rows.append(row)
            continue
        cfg = read(cfg_path, bindings)
        if any(cfg.get(k) != c[k] for k in ('dataset', 'realization', 'order', 'arm', 'items')):
            raise ValueError('plan/config coordinates differ')
        if cfg['sources'] != plan['sources']:
            raise ValueError('plan/config sources differ')
        if not smoke and bool(cfg.get('diagnostic')) != diagnostic:
            raise ValueError('diagnostic/replication mode differs')
        if not smoke and cfg['population'] != ('development' if diagnostic else 'exposed historical S5; supplemental defect-correction replication'):
            raise ValueError('config population differs')
        for name, digest in cfg['sources'].items():
            verify(name, digest, bindings)
        if smoke:
            verify(cfg['weights_path'], cfg['weights_sha256'], bindings)
        else:
            from aw.pc_v0 import ARCHIVE, ARCHIVE_SHA, WEIGHTS_SHA
            verify(ARCHIVE, ARCHIVE_SHA, bindings)
            archive = json.loads(ARCHIVE.read_bytes())
            if cfg['weights_sha256'] != WEIGHTS_SHA or cfg['credit_iters'] != 8 or cfg['error_lr'] != .1:
                raise ValueError('model or credit settings differ from specification')
            verify(archive['base_checkpoints']['epc']['path'], WEIGHTS_SHA, bindings)
            from pccap.bases import gpt2_jax as g
            verify(g.DEFAULT_SNAPSHOT / 'tokenizer.json', archive['tokenizer_rev']['tokenizer_json_sha256'], bindings)
        manifest = cfg.get('manifest', ROOT / f'manifests/dev/{ds}_dev.json')
        verify(manifest, cfg['manifest_sha256'], bindings)
        verify(cfg['drift']['path'], cfg['drift']['sha256'], bindings)
        row['pair_identity'] = {k: cfg[k] for k in ('weights_sha256', 'manifest_sha256', 'sources', 'item_ids',
                                                    'locality_prompts_sha256', 'base_hash_before', 'initial_state',
                                                    'error_lr', 'credit_iters', 'drift')}
        row['pair_identity']['named_seeds'] = cfg.get('named_seeds')
        if not finish_path.exists():
            row['status'] = 'unfinished'
            rows.append(row)
            continue
        finish = read(finish_path, bindings)
        row.update(status=finish['status'], finish=finish)
        if finish.get('base_hash_after') is not None and not (finish['base_hash_after'] == finish['base_hash_before'] == cfg['base_hash_before']):
            raise ValueError('base changed within cell')
        if finish['status'] == 'complete' and finish.get('base_hash_after') is None:
            raise ValueError('complete cell lacks base identity check')
        finite(finish['elapsed_process_seconds'])
        if (dest / 'diagnostics.json').exists():
            if not diagnostic:
                raise ValueError('diagnostic is not a replication cell')
            row['diagnostics'] = read(dest / 'diagnostics.json', bindings)
            for sample in row['diagnostics']['rows']:
                if [d['iters'] for d in sample['diagnostics']] != [1, 8, 32]:
                    raise ValueError('diagnostic horizon inventory differs')
                for d in sample['diagnostics']:
                    if len(d['energies']) != d['iters'] + 1:
                        raise ValueError('diagnostic energy trace length differs')
                    for energy in d['energies']:
                        finite(energy)
        elif (dest / 'metrics.json').exists():
            metrics = read(dest / 'metrics.json', bindings)
            if metrics['status'] != finish['status'] or metrics['items_completed'] != finish['items_completed']:
                raise ValueError('finish/metrics disposition differs')
            if metrics['items_planned'] != c['items'] or (finish['status'] == 'complete' and metrics['items_completed'] != c['items']):
                raise ValueError('complete cell has incomplete item grid')
            row['metrics'] = {name: finite(metrics['metrics'][key]['value']) for name, key in METRICS.items()}
            secondary = read(dest / 'secondary-summary.json', bindings)
            if secondary['items_completed'] != metrics['items_completed'] or secondary['items_planned'] != c['items']:
                raise ValueError('secondary item counts differ')
            row['secondary'] = {k: finite(secondary[k]) for k in SECONDARY}
            row['items_completed'] = metrics['items_completed']
        elif finish['status'] == 'complete':
            raise ValueError('complete cell has no metrics/diagnostics')
        rows.append(row)
    if (path / 'summary.json').exists():
        summary = read(path / 'summary.json', bindings)
        if summary['planned'] != len(plan['cells']):
            raise ValueError('group count differs')
        for entry in summary['finished']:
            match = [r for r in rows if coordinate(r) == coordinate(entry['cell'])]
            if len(match) != 1 or entry['finish'] != match[0].get('finish'):
                raise ValueError('group/cell finish differs')
    return rows


def compare(rows, expected):
    indexed = {coordinate(r): r for r in rows}
    if len(indexed) != len(rows):
        raise ValueError('duplicate cell across run groups; select a single attempt explicitly')
    if set(indexed) - {coordinate(c) for c in expected}:
        raise ValueError('cell outside preselected design')
    cells = [indexed.get(coordinate(c), dict(c, status='missing', metrics={}, secondary={})) for c in expected]
    pairs = []
    for c in cells:
        if c['arm'] != 'SE-A':
            continue
        e = next(x for x in cells if coordinate(x) == (*coordinate(c)[:3], 'SE-E'))
        if 'pair_identity' in c and 'pair_identity' in e and c['pair_identity'] != e['pair_identity']:
            raise ValueError('paired arms differ in model/data/seeds/initial state')
        complete = c['status'] == e['status'] == 'complete'
        pairs.append(dict(dataset=c['dataset'], realization=c['realization'], order=c['order'],
                          status='complete' if complete else f"SE-A={c['status']}; SE-E={e['status']}",
                          difference={k: e['metrics'][k] - c['metrics'][k] if complete and e['metrics'].get(k) is not None and c['metrics'].get(k) is not None else None for k in METRICS},
                          secondary_difference={k: e['secondary'][k] - c['secondary'][k] if complete and e['secondary'].get(k) is not None and c['secondary'].get(k) is not None else None for k in SECONDARY}))
    aggregates = []
    for ds in ('zsre', 'counterfact'):
        for k in (*METRICS, *SECONDARY):
            field = 'difference' if k in METRICS else 'secondary_difference'
            rs = []
            for r in range(3):
                values = [p[field][k] for p in pairs if p['dataset'] == ds and p['realization'] == r]
                rs.append(statistics.mean(values) if values and all(v is not None for v in values) else None)
            full = all(v is not None for v in rs)
            aggregates.append(dict(dataset=ds, metric=k, realizations=rs, mean=statistics.mean(rs) if full else None,
                                   minimum=min(rs) if full else None, maximum=max(rs) if full else None))
    return cells, pairs, aggregates


def table(headers, rows):
    def fmt(x):
        return 'unavailable' if x is None else f'{x:.6g}' if isinstance(x, float) else str(x)
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(fmt(x) for x in row) + ' |' for row in rows]) + '\n\n'


def build(groups, output, document, *, orders=1, smoke=False, diagnostics=()):
    bindings = {}
    rows = [r for p in groups for r in load_group(p, bindings, smoke=smoke)]
    expected = expected_cells(orders)
    if smoke and groups:
        # Tiny runner smoke has a deliberately small, explicitly synthetic design.
        expected = read(Path(groups[0]) / 'plan.json', bindings)['cells']
    cells, pairs, aggregates = compare(rows, expected)
    diagnostic_rows = [r for p in diagnostics for r in load_group(p, bindings, smoke=smoke, diagnostic=True)]
    spec = ROOT / 'docs/additional_work/PC-v0.md'
    bindings[str(spec)] = sha(spec)
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    report = dict(smoke=smoke, cells=cells, pairs=pairs, aggregates=aggregates, diagnostics=diagnostic_rows,
                  sources_sha256=bindings, expected_cells=len(expected), historical=dict(ES=-.336, RET_GS=.019,
                  scope='Historical defective-energy reference, zsRE; not pooled with corrected results', source=str(spec)))
    output, document = Path(output), Path(document)
    output.mkdir(parents=True, exist_ok=False)
    document.parent.mkdir(parents=True, exist_ok=True)
    (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    for name, values in (('pairs', pairs), ('aggregates', aggregates)):
        with (output / f'{name}.csv').open('x', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(values[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in values)
    title = '# PC-v0 corrected-credit comparison' + (' — CPU SMOKE ONLY' if smoke else '')
    text = title + '\n\n' + ('Synthetic tiny-model smoke; no research result.\n\n' if smoke else '')
    text += f"{sum(c['status'] == 'complete' for c in cells)}/{len(cells)} planned cells complete. Missing/partial cells remain explicit. Complete-pair differences only; no partial-prefix scores enter the paired estimate.\n\n"
    text += 'SE-E minus SE-A; old S5 scoring. Secondary bounded-text scores remain separate. Exposed S5 populations are supplemental defect-correction replication, not fresh confirmation.\n\n'
    text += 'Presentation context: this credit-rule comparison is a measured component toward the active-inference programme. It does not implement expected-free-energy policy selection. Heavy-tailed-distribution questions require the companion distributional harm measurements; editing accuracy alone cannot answer them. See docs/presentation/presentation_brief_2026-09-26.md.\n\n'
    text += table(['Dataset', 'r', 'order', 'status', *METRICS, *SECONDARY], [[p['dataset'], p['realization'], p['order'], p['status'], *p['difference'].values(), *p['secondary_difference'].values()] for p in pairs])
    text += '## Realization summaries\n\nOrder differences are averaged within each realization. Only a complete three-realization design receives an overall mean/range. The range is descriptive, not a confidence interval; tokens and orders are not independent replicates.\n\n'
    text += table(['Dataset', 'metric', 'r0, r1, r2', 'mean', 'min', 'max'], [[a['dataset'], a['metric'], a['realizations'], a['mean'], a['minimum'], a['maximum']] for a in aggregates])
    text += '## Historical reference and limitations\n\nDefective-energy historical zsRE SE-E − SE-A: ES −0.336, RET-GS +0.019 (specification of record, docs/additional_work/PC-v0.md). It is not a corrected-energy control or fresh replication. CounterFact had a historical paraphrase floor of zero. No κ, coupled-free-energy, or general PC-superiority claim follows.\n\n'
    text += '## Cost\n\nProcess seconds include startup/compilation; sums are not GPU elapsed hours. Counts are actual ledger totals. Eight-step error credit requires 9 forwards + 9 reverses per inference call; an adjoint call costs 1 forward + 1 reverse. Totals also include prediction, acceptance and diagnostics. Operation totals do not identify the number of credit calls.\n\n'
    cost_rows = []
    for c in cells:
        f = c.get('finish', {})
        total = f.get('ledger', {}).get('total', {})
        cost_rows.append([c['dataset'], c['realization'], c['order'], c['arm'], c['status'], f.get('elapsed_process_seconds'), total.get('full_forwards'), total.get('reverses'), total.get('settle_iters')])
    text += table(['Dataset', 'r', 'order', 'arm', 'status', 'process seconds', 'forwards', 'reverses', 'settle iterations'], cost_rows)
    text += '## Development 1/8/32 diagnostic\n\n'
    ds = []
    for c in diagnostic_rows:
        for row in c.get('diagnostics', {}).get('rows', []):
            for d in row['diagnostics']:
                for site in d['sites']:
                    ds.append([c['dataset'], row['item_id'], len(row['prefix_ids']), row['writes'], d['iters'], site['bank'], d['energies'][0], d['energies'][-1], d['gradient_norm_0'], d['gradient_norm_k'], d['r_k'], site['cosine_to_negative_adjoint'], site['norm_ratio']])
    text += table(['Dataset', 'item', 'prefix length', 'writes', 'iters', 'bank', 'E0', 'Ek', 'grad0', 'gradk', 'residual ratio', 'cosine', 'norm ratio'], ds) if ds else 'Unavailable: no development diagnostic group supplied.\n\n'
    text += 'Companion matched-position ordinary-text harm readout: unavailable until separately measured; this generator does not infer it from editing scores.\n\nIdentity checks verify recorded model/data/source hashes against local bytes and paired configs. The runner does not pre-sign metric/config files: this report binds their present bytes, not their historical authenticity.\n'
    document.write_text(text)
    (output / 'publication.json').write_text(json.dumps({'document':str(document.resolve()), 'sha256':sha(document)}, indent=2)+'\n')
    return report


def plot(report_path, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    report = json.loads(Path(report_path).read_bytes())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
    for ax, ds in zip(axes, ('zsre', 'counterfact')):
        for arm, marker in (('SE-A', 'o'), ('SE-E', '^')):
            xs, ys, labels = [], [], []
            for r in range(3):
                cells = [c for c in report['cells'] if c['dataset'] == ds and c['arm'] == arm and c['realization'] == r]
                if cells and all(c['status'] == 'complete' and c['metrics'].get('RET-GS') is not None for c in cells):
                    xs.append(statistics.mean(c['finish']['elapsed_process_seconds'] for c in cells))
                    ys.append(statistics.mean(c['metrics']['RET-GS'] for c in cells))
                    labels.append(r)
            ax.scatter(xs, ys, marker=marker, label=arm)
            for x, y, r in zip(xs, ys, labels):
                ax.annotate(f'r{r}', (x, y), xytext=(4, 4), textcoords='offset points')
        if not ax.collections or not any(len(c.get_offsets()) for c in ax.collections):
            ax.text(.5, .5, 'Results pending', transform=ax.transAxes, ha='center')
        ax.set(title=ds, xlabel='Mean process seconds / cell', ylim=(-.04, 1.04))
        ax.legend()
    axes[0].set_ylabel('RET-GS (fraction)')
    fig.suptitle('PC-v0: efficacy and measured cost' + (' — CPU SMOKE' if report['smoke'] else ''))
    fig.tight_layout()
    exports = []
    for ext in ('png', 'pdf', 'svg'):
        p = output / f'efficacy-cost.{ext}'
        fig.savefig(p, dpi=150)
        exports.append(dict(path=str(p.resolve()), sha256=sha(p)))
    plt.close(fig)
    (output / 'manifest.json').write_text(json.dumps(dict(report=dict(path=str(Path(report_path).resolve()), sha256=sha(report_path)), exports=exports), indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('build', 'plot'))
    p.add_argument('--run', action='append', default=[])
    p.add_argument('--diagnostic-group', action='append', default=[])
    p.add_argument('--orders', type=int, choices=(1, 5), default=1)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--output', required=True)
    p.add_argument('--document', default=str(ROOT / 'docs/additional_work/PC-v0_report.md'))
    p.add_argument('--report')
    a = p.parse_args()
    if a.command == 'build':
        r = build(a.run, a.output, a.document, orders=a.orders, smoke=a.smoke, diagnostics=a.diagnostic_group)
        print(json.dumps({'cells': len(r['cells']), 'complete': sum(c['status']=='complete' for c in r['cells'])}))
    else:
        plot(a.report, a.output)


if __name__ == '__main__':
    main()
