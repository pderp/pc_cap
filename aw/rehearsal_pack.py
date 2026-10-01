"""PRES-8: resolved deck, timing, backup index and sourced rehearsal numbers."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from aw.pc_historical import ROOT, sha
from aw.presentation_slides import export
from aw.presentation_timing import main as timing


def build(output):
    output = Path(output).resolve()
    log = ROOT / 'logs/additional_work/PRES-8'
    timing(refresh=True, log_dir=log)
    deck = export(output)
    timing_path = log / 'presentation-timing.json'
    shutil.copyfile(timing_path, output / 'timings.json')
    shutil.copyfile(ROOT / 'docs/presentation/qa.md', output / 'qa.md')
    backup = {
        'HT-17 survival: empirical curves, invalid-fit caveats': ROOT.parent / 'assets/presentation-materials/figures/tails_ht17/snapshot-20261001-v2/survival_thresholds.png',
        'κ pilot: retention versus tail trade-off, declared gate failed': ROOT / 'logs/r1_round37/presentation-figures-v2/kappa-tradeoff.png',
        'PC controls: depth, retention, harm and cost': ROOT.parent / 'assets/presentation-materials/figures/pc_v0/controls/depth-retention-harm-cost.png',
    }
    lines=['# Backup-slide index', '', 'Use after the timed script, or on request; these figures do not add time to its 15/25-minute budget.', '']
    sources={str(timing_path):sha(timing_path)}
    for label, original in backup.items():
        target=output / original.name
        shutil.copyfile(original,target)
        sources[str(original)]=sha(original)
        lines.append(f'- [{label}]({target.name}).')
    lines += ['', 'HT-17: finite-range shapes, not classes; shape intervals condition on fixed cells and assume adequate window blocks. κ pilot: development population, 4,064 positions and ES95; do not compare it directly with Stage-4 ES99. PC controls: order100 subset; offered-budget adjoint did not spend all available compute.']
    (output/'backup-index.md').write_text('\n'.join(lines)+'\n')
    reader_path=ROOT/'logs/additional_work/PC-reader/report-round57-final/report.json'
    ht_path=ROOT/'logs/additional_work/HT-17/snapshot-20261001-v2/report.json'
    stage_path=ROOT/'logs/R1/reports/triplet/summary.json'
    reader=json.loads(reader_path.read_bytes())
    ht=json.loads(ht_path.read_bytes())
    stage=json.loads(stage_path.read_bytes())
    def severity(ds,condition):
        return next(r for r in ht['groups'] if r['phase']=='AW-B' and r['dataset']==ds and r['condition']==condition)['thresholds']['0.01']['conditional_mean_loss']
    def retention(ds):
        rows=[r for r in stage['groups'] if r['condition']=='R1_learned_ff' and r['dataset']==ds]
        values=[v for r in rows for v in r['primary']['RET-GS']]
        return sum(values)/len(values)
    ratio=next(r['epc_over_bp'] for r in reader['training_cost_ratios'] if r['seed']==0)
    text=f'''# Numbers to say — October 1 evidence snapshot

Use rounded values below. These are measured results or explicitly labeled scope; no pending value is zero. Source keys refer to the precise records below and to `manifest.json`/`rehearsal-manifest.json` for hashes.

- **Main learned-reader paraphrase retention:** zsRE **{100*retention('zsre'):.1f}%**, CounterFact **{100*retention('counterfact'):.1f}%** after 1,000 edits; MQuAKE **{100*retention('mquake'):.1f}%** at its separate 300-edit endpoint. Three realizations, five dependent orders each. [S]
- **Fidelity:** all **45/45** main learned-reader cells exceed mean KL **0.001**. Integrity and preservation are different checks. [S]
- **AW-B mixture severity:** zsRE **{severity('zsre','v5'):.3f}→{severity('zsre','mixture:0.367879'):.3f} nats**; CounterFact **{severity('counterfact','v5'):.3f}→{severity('counterfact','mixture:0.367879'):.3f}** conditional on loss increase >.01 nat. Roughly one-third, not half; harmful-change frequency is nearly unchanged. Ten exposed 300-edit memories, five orders/dataset. [H]
- **Analytic mixture ceiling:** **one nat per token at the same prefix** for base weight exp(−1). Not a one-nat whole-answer guarantee. [B]
- **PC-reader:** **8/12** evaluations available; only seed0 paired. Completed ePC/BP training process-time ratio **{ratio:.1f}×**; 37× was a forecast. No three-seed finding yet. [P]
- **Main execution:** **270 cells, 392.42 process-hours**. Concurrent process time, not elapsed GPU time; supplemental work is additional. **GPT-2 small, 124M**; transfer to production scale unestablished. [A]
- **Schedule:** experiment cutoff **October 9, 17:00 EDT**; presentation **October 15**. [A]

[S] `logs/R1/reports/triplet/summary.json`: learned condition, dataset, `primary.RET-GS`; benchmark counts per group.
[H] `logs/additional_work/HT-17/snapshot-20261001-v2/report.json`: AW-B groups, threshold .01, `conditional_mean_loss`.
[B] `docs/additional_work/AW-B_report.md`: declared mixture and scope.
[P] `logs/additional_work/PC-reader/report-round57-final/report.json`: coverage and `training_cost_ratios[seed=0]`.
[A] `docs/R1_stage4_report.md`: accounting and limitations.

For detailed PC effects use the resolved scripts' source slots. Do not improvise a favorable PC conclusion, an asymptotic tail class, W(N), or a completed Option R/upper-layer result. Refresh after new evaluations and the October 2 review.
'''
    (output/'numbers-to-say.md').write_text(text)
    (ROOT/'docs/presentation/numbers_to_say.md').write_text(text)
    for p in (reader_path, ht_path, stage_path, ROOT/'docs/additional_work/AW-B_report.md', ROOT/'docs/R1_stage4_report.md', ROOT/'docs/presentation/qa.md', Path(__file__).resolve()):
        sources[str(p)]=sha(p)
    index='''# Rehearsal pack — charlie's October 15 presentation

Canonical October 1 export: `assets/presentation-materials/deck_v3/rehearsal/`.

- `speaking-script-15min.md` and `speaking-script-25min.md`: resolved numbers, per-slide clocks, cuts and evidence.
- `timings.json`: allocations total exactly 15/25 minutes, including slide changes but excluding Q&A. Rates are estimates, not a measured rehearsal or confirmed session duration.
- `slide1.svg` through `slide12.svg`: current deck with model-scale and omitted-arm caveats.
- `qa.md`, `numbers-to-say.md`, `backup-index.md`: audience answers, one-page numerical prompts and three figures for follow-up questions.
- `manifest.json` binds deck inputs; `rehearsal-manifest.json` binds this entire pack. No private author-equation question is exported.

The October 2 review notes have not arrived. Refresh PC-reader after seeds1–2, Option R after resume, and AW-L after its queue; update their literal text as well as generated tables. No three-seed or completed-extension conclusion should be inferred from this snapshot.
'''
    (output/'README.md').write_text(index)
    (ROOT/'docs/presentation/rehearsal.md').write_text(index)
    manifest=dict(task='PRES-8',sources_sha256=sources,deck_manifest_sha256=sha(output/'manifest.json'),
                  exports={str(p):sha(p) for p in sorted(output.iterdir()) if p.is_file()},
                  draft=True,review_notes_pending=True,script_slots_unresolved=0)
    for p in output.glob('speaking-script-*.md'):
        if '{{' in p.read_text() or 'PENDING' in p.read_text().split('## Cut and backup')[0].split('Say:',1)[1]:
            raise ValueError('unresolved result slot in speaking script')
    (output/'rehearsal-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (log/'pack.json').write_text(json.dumps(dict(output=str(output),manifest_sha256=sha(output/'rehearsal-manifest.json'),exports=len(manifest['exports']),deck_sources=len(deck['sources_sha256'])),indent=2)+'\n')
    print(json.dumps(dict(exports=len(manifest['exports']),deck_sources=len(deck['sources_sha256']))))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    build(parser.parse_args().output)
