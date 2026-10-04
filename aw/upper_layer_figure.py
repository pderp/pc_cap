"""Plot every completed AW-L seed; no model calls or new fits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aw.reader_results import sha


def render(report, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    report, output = Path(report).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError('new figure directory required')
    r = json.loads(report.read_text())
    if r['completed_evaluations'] != 24:
        raise ValueError('complete factorial required for this figure')
    cells = {(c['dataset'], c['seed'], c['planned_read'], c['planned_write']): c
             for c in r['cells'] if c['status'] == 'complete'}
    coordinates = [('all', 'all'), ('all', 'last'), ('upper', 'all'), ('upper', 'last')]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    for j, ds in enumerate(('zsre', 'counterfact')):
        for seed in range(3):
            rows = [cells[ds, seed, read, write] for read, write in coordinates]
            label = f'seed {seed}'
            axes[0, j].plot(range(4), [100*c['metrics']['RET-GS']['value'] for c in rows],
                            'o-', label=label)
            axes[1, j].plot(range(4), [c['harm']['capoff']['mean_delta_nll'] for c in rows],
                            'o-', label=label)
        axes[0, j].set_title(ds if ds == 'zsre' else 'CounterFact')
        axes[0, j].set_ylabel('Paraphrase retention (%) — higher is better')
        axes[1, j].set_ylabel('Mean ΔNLL (nats) — lower is better')
        axes[1, j].set_yscale('log')
        for ax in axes[:, j]:
            ax.set_xticks(range(4), ['all / all', 'all / last', 'upper / all', 'upper / last'])
            ax.set_xlabel('Read taps / write sites')
            ax.grid(alpha=.2)
            ax.legend(fontsize=8)
    fig.suptitle('Upper-layer interfaces: useful retention and unintended harm', fontsize=14)
    fig.text(.5, .015,
             'Three training seeds · exposed realization 0 · 300 edits · 245,237 positions/cell\n'
             'All readers trained with full-write objective; all/all controls reused from PC-reader. '
             'Lines join paired seeds, not independent populations; no confidence intervals.',
             ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .065, 1, .95))
    output.mkdir(parents=True)
    exports = {}
    for suffix in ('png', 'svg', 'pdf'):
        path = output / f'upper-layer-tradeoffs.{suffix}'
        fig.savefig(path, dpi=180, bbox_inches='tight')
        exports[str(path)] = sha(path)
    plt.close(fig)
    manifest = dict(source=dict(path=str(report), sha256=sha(report)),
                    generator=dict(path=str(Path(__file__).resolve()), sha256=sha(__file__)),
                    exports=exports, selection='all 24 cells; each seed shown', gpu_seconds=0)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    render(a.report, a.output)


if __name__ == '__main__':
    main()
