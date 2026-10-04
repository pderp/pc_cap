"""PRES-8: resolved deck, timing, backup index and sourced rehearsal numbers."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from aw.pc_historical import ROOT, sha
from aw.presentation_slides import export
from aw.presentation_timing import main as timing
from aw.refresh_report_steps import reader_number_line


def build(output):
    output = Path(output).resolve()
    log = ROOT / 'logs/additional_work/PRES-8'
    timing(refresh=True, log_dir=log)
    deck = export(output)
    timing_path = log / 'presentation-timing.json'
    shutil.copyfile(timing_path, output / 'timings.json')
    shutil.copyfile(ROOT / 'docs/presentation/qa.md', output / 'qa.md')
    backup = {
        'HT-17 survival: empirical curves, invalid-fit caveats': ROOT.parent / 'assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/survival_thresholds.png',
        'κ pilot: retention versus tail trade-off, declared gate failed': ROOT / 'logs/r1_round37/presentation-figures-v2/kappa-tradeoff.png',
        'PC controls: depth, retention, harm and cost': ROOT.parent / 'assets/presentation-materials/figures/pc_v0/controls/depth-retention-harm-cost.png',
        'Upper-layer factorial: every seed, retention and harm': ROOT.parent / 'assets/presentation-materials/figures/upper_layer/round63-complete/upper-layer-tradeoffs.png',
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
    reader_path=ROOT/'logs/additional_work/PC-reader/report-round63-final/report.json'
    ht_path=ROOT/'logs/additional_work/HT-17/snapshot-20261004-complete/report.json'
    stage_path=ROOT/'logs/R1/reports/triplet/summary.json'
    reader=json.loads(reader_path.read_bytes())
    ht=json.loads(ht_path.read_bytes())
    stage=json.loads(stage_path.read_bytes())
    r_path=ROOT/'logs/additional_work/R/report-round63-final/report.json'
    l_path=ROOT/'logs/additional_work/AW-L/report-round63-final/report.json'
    extension=json.loads(r_path.read_bytes())
    upper=json.loads(l_path.read_bytes())
    extension_final=[x for x in extension['sensitivity'] if x['checkpoint']==1000 and x['metric']=='RET-GS']
    extension_numbers='; '.join(f"{x['dataset']} **{100*x['estimate']:.2f} percentage points**" for x in extension_final)
    write_ratios=[x['mean_loss_ratio'] for x in upper['write_comparisons'] if x['mean_loss_ratio'] is not None]
    def severity(ds,condition):
        return next(r for r in ht['groups'] if r['phase']=='AW-B' and r['dataset']==ds and r['condition']==condition)['thresholds']['0.01']['conditional_mean_loss']
    def retention(ds):
        rows=[r for r in stage['groups'] if r['condition']=='R1_learned_ff' and r['dataset']==ds]
        values=[v for r in rows for v in r['primary']['RET-GS']]
        return sum(values)/len(values)
    text=f'''# Numbers to say — October 4 evidence snapshot

Use rounded values below. These are measured results or explicitly labeled scope; no pending value is zero. Source keys refer to the precise records below and to `manifest.json`/`rehearsal-manifest.json` for hashes.

- **Main learned-reader paraphrase retention:** zsRE **{100*retention('zsre'):.1f}%**, CounterFact **{100*retention('counterfact'):.1f}%** after 1,000 edits; MQuAKE **{100*retention('mquake'):.1f}%** at its separate 300-edit endpoint. Three realizations, five dependent orders each. [S]
- **Fidelity:** all **45/45** main learned-reader cells exceed mean KL **0.001**. Integrity and preservation are different checks. [S]
- **AW-B mixture severity:** zsRE **{severity('zsre','v5'):.3f}→{severity('zsre','mixture:0.367879'):.3f} nats**; CounterFact **{severity('counterfact','v5'):.3f}→{severity('counterfact','mixture:0.367879'):.3f}** conditional on loss increase >.01 nat. Roughly one-third, not half; harmful-change frequency is nearly unchanged. Ten exposed 300-edit memories, five orders/dataset. [H]
- **Analytic mixture ceiling:** **one nat per token at the same prefix** for base weight exp(−1). Not a one-nat whole-answer guarantee. [B]
{reader_number_line(reader)}
- **Option R:** **20 complete, 1 incomplete, 9 deferred**; four-realization learned−random paraphrase sensitivity: {extension_numbers}. Unadjusted t(3), assumed normal realization errors; not a reissued classifier. [R]
- **Upper-layer writes:** last-only mean-loss ratio **{min(write_ratios):.2f}–{max(write_ratios):.2f}×** all-write across twelve paired comparisons; **24 cells**, six shared controls. All readers trained with full-write objective. [L]
- **Main execution:** **270 cells, 392.42 process-hours**. Concurrent process time, not elapsed GPU time; supplemental work is additional. **GPT-2 small, 124M**; transfer to production scale unestablished. [A]
- **Schedule:** experiment cutoff **October 9, 17:00 EDT**; presentation **October 15**. [A]

[S] `logs/R1/reports/triplet/summary.json`: learned condition, dataset, `primary.RET-GS`; benchmark counts per group.
[H] `{ht_path}`: AW-B groups, threshold .01, `conditional_mean_loss`.
[B] `docs/additional_work/AW-B_report.md`: declared mixture and scope.
[P] `{reader_path}`: coverage, per-seed endpoint numerators/denominators and `training_cost_ratios` for completed trainings.
[A] `docs/R1_stage4_report.md`: accounting and limitations.
[R] `{r_path}`: inventory and final-checkpoint sensitivity.
[L] `{l_path}`: write comparisons and cost-gate disclosure.

Detailed spoken numbers use `docs/talk_claim_ledger_v7.md` and `docs/presentation/deck_v3/pc-result-sources.json`. Rerun `aw.script_numbers_check` after every export; its occurrence inventory states rounding tolerances and untraced/review items. Numerical ledger matches alone do not establish contextual correctness. Do not improvise a favorable PC conclusion, an asymptotic tail class or W(N). The October 2 review requested no changes to the programme or framing (DEC-082). Planned GPU work completed October 4; charlie's freeze review remains.
'''
    (output/'numbers-to-say.md').write_text(text)
    (ROOT/'docs/presentation/numbers_to_say.md').write_text(text)
    for p in (reader_path, ht_path, stage_path, r_path, l_path, ROOT/'docs/additional_work/AW-B_report.md', ROOT/'docs/R1_stage4_report.md', ROOT/'docs/presentation/qa.md', ROOT/'docs/friday-10.02-review/OUTCOME-2026-10-02.md', ROOT/'aw/refresh_report_steps.py', Path(__file__).resolve()):
        sources[str(p)]=sha(p)
    index='''# Rehearsal pack — charlie's October 15 presentation

Canonical October 4 export: `assets/presentation-materials/deck_v3/rehearsal/`.

- `speaking-script-15min.md` and `speaking-script-25min.md`: resolved numbers, per-slide clocks, cuts and evidence.
- `timings.json`: allocations total exactly 15/25 minutes, including slide changes but excluding Q&A. Rates are estimates, not a measured rehearsal or confirmed session duration.
- `slide1.svg` through `slide12.svg`: current deck with model-scale and omitted-arm caveats.
- `qa.md`, `numbers-to-say.md`, `backup-index.md`: audience answers, one-page numerical prompts and four figures for follow-up questions.
- `manifest.json` binds deck inputs; `rehearsal-manifest.json` binds this entire pack. No private author-equation question is exported.

The October 2 review is resolved: no changes requested to the remaining experiments or approved talk framing (DEC-082). The optional κ readout is closed without execution; coupled-objective work is a post-conference proposal. Outcome: https://github.com/pderp/pc_cap/blob/master/docs/friday-10.02-review/OUTCOME-2026-10-02.md

PC-reader has 12/12 evaluations and three paired seeds. Option R has twenty complete learned/random cells, one v0 ceiling stop and nine deferred v0 cells. AW-L has all 24 cells, including six shared controls. GPU work finished October 4; final source checks and charlie's October 9 freeze review remain. Three training seeds do not establish population-wide generalization.
'''
    (output/'README.md').write_text(index)
    (ROOT/'docs/presentation/rehearsal.md').write_text(index)
    manifest=dict(task='PRES-8',sources_sha256=sources,deck_manifest_sha256=sha(output/'manifest.json'),
                  exports={str(p):sha(p) for p in sorted(output.iterdir()) if p.is_file()},
                  draft=True,review_notes_pending=False,review_outcome='DEC-082: no changes requested',script_slots_unresolved=0)
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
