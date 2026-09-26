"""PRES-1: export the three-theme outline, source figures and measured claim ledger."""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
from pathlib import Path

from aw.pc_v0_report import sha, table

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT.parent/'assets'


def svg(title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="640" viewBox="0 0 1200 640">
<rect width="1200" height="640" fill="#faf9f5"/>
<style>text{{font-family:Arial,sans-serif;fill:#18252e}} .title{{font-size:32px;font-weight:bold}} .head{{font-size:24px;font-weight:bold}} .line{{font-size:19px}} .note{{font-size:17px;fill:#465763}}</style>
<text x="48" y="60" class="title">{title}</text>{body}</svg>'''


def diagrams(directory):
    questions=svg('Active Inference in the Extremes', '''
<text x="48" y="103" class="line">Three questions connect the programme to the experiments</text>
<rect x="45" y="148" width="350" height="326" rx="16" fill="#e0ecef"/>
<rect x="425" y="148" width="350" height="326" rx="16" fill="#e5eddd"/>
<rect x="805" y="148" width="350" height="326" rx="16" fill="#f3e5d6"/>
<text x="65" y="192" class="head">Active inference</text>
<text x="65" y="246" class="line">What should the agent</text><text x="65" y="275" class="line">learn or do next?</text>
<text x="65" y="338" class="line">Beliefs, preferences,</text><text x="65" y="367" class="line">outcomes and information</text>
<text x="65" y="435" class="note">Programme and next mechanisms</text>
<text x="445" y="192" class="head">Predictive coding</text>
<text x="445" y="246" class="line">Can iterative error inference</text><text x="445" y="275" class="line">supply useful learning credit?</text>
<text x="445" y="338" class="line">Corrected SE-E vs SE-A:</text><text x="445" y="367" class="line">efficacy, harm and cost</text>
<text x="445" y="435" class="note">Paired experimental question</text>
<text x="825" y="192" class="head">Heavy-tailed distributions</text>
<text x="825" y="246" class="line">What can a mean conceal</text><text x="825" y="275" class="line">about rare consequences?</text>
<text x="825" y="338" class="line">Exceedances, maxima,</text><text x="825" y="367" class="line">concentration and trade-offs</text>
<text x="825" y="435" class="note">Measured distributional evidence</text>
<text x="48" y="538" class="line">A small adaptive system on a frozen prior is our testbed.</text>
<text x="48" y="577" class="note">Conceptual framing: observed concentration alone does not establish a heavy-tail family.</text>''')
    programme=svg('From the active-inference programme to the testbed', '''
<rect x="45" y="160" width="280" height="220" rx="16" fill="#e0ecef"/>
<rect x="460" y="160" width="280" height="220" rx="16" fill="#e5eddd"/>
<rect x="875" y="160" width="280" height="220" rx="16" fill="#f3e5d6"/>
<text x="64" y="202" class="head">Environment / data</text>
<text x="64" y="250" class="line">Supplied factual edits</text><text x="64" y="282" class="line">Queries and ordinary text</text><text x="64" y="336" class="note">Controlled streams and assays</text>
<text x="479" y="202" class="head">Adaptive cap</text>
<text x="479" y="250" class="line">Memory + reader/null gate</text><text x="479" y="282" class="line">Bounded residual writes</text><text x="479" y="336" class="note">Credit: adjoint or PC treatment</text>
<text x="894" y="202" class="head">Frozen transformer</text>
<text x="894" y="250" class="line">Predictions and features</text><text x="894" y="282" class="line">Base weights stay fixed</text><text x="894" y="336" class="note">A generative prior / substrate</text>
<path d="M325 243 H450 M440 237 L450 243 L440 249 M460 304 H335 M345 298 L335 304 L345 310 M740 304 H865 M855 298 L865 304 L855 310 M875 243 H750 M760 237 L750 243 L760 249" stroke="#465763" stroke-width="3" fill="none"/>
<text x="340" y="229" class="note">observations</text><text x="342" y="330" class="note">predictions</text>
<text x="752" y="229" class="note">features</text><text x="753" y="330" class="note">writes</text>
<rect x="45" y="430" width="1110" height="118" rx="12" fill="none" stroke="#617481" stroke-width="2" stroke-dasharray="8 6"/>
<text x="65" y="468" class="head">Proposed active-inference extension</text>
<text x="65" y="503" class="line">Preferences + policy inference + information-seeking audits; coupled boundary/objective hypotheses</text>
<text x="48" y="590" class="note">Interfaces are implemented. Expected-free-energy policy choice and blanket theorems are not established.</text>''')
    for name,text in (('three-questions.svg',questions),('programme-and-testbed.svg',programme)):
        (directory/name).write_text(text)


def ledger(comparators):
    report=json.loads(Path(comparators).read_bytes())
    native=json.loads(Path(report['analysis']['path']).read_bytes())
    pc4=json.loads((ROOT/'results/additional_work/PC-4/devcheckpoint.json').read_bytes())
    review=json.loads((ROOT/'logs/r1_round22/ht3e-independent-review-v2.json').read_bytes())
    rows=[]
    def add(identity,theme,status,result,population,control,supports,limits,source):
        rows.append(dict(id=identity,theme=theme,status=status,measured_result=result,population=population,
                         control=control,supports=supports,does_not_support=limits,source=source))
    add('AI-programme','Active inference','proposed','—','Abstract programme; no experimental population','Not an experimental comparison',
        'A frozen prior and adaptive residual system motivate a future belief/action/audit loop',
        'Expected-free-energy policy selection, proved blankets, coupled free energy or one-κ equivalence are not implemented conclusions',
        'docs/presentation/presentation_brief_2026-09-26.md; errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf')
    for ds in ('zsre','counterfact','mquake'):
        gr=[r for r in report['groups'] if r['dataset']==ds and r['condition']=='R1_learned_ff']
        gs=[statistics.mean(r['primary']['RET-GS']) for r in gr]
        add(f'R1-retention-{ds}','Active inference testbed / PC context','measured',
            f"RET-GS mean {statistics.mean(gs):.6f}; realization means {gs}",
            f"{ds}; 3 realizations × 5 orders; {gr[0]['checkpoint']} edits",'Random reader and stable v0 in the same matrix',
            'Useful paraphrase retention on the tested populations',
            'Not PC credit, active policy selection, frontier-scale transfer or population-wide superiority; MQuAKE at 300 is descriptive',report['analysis']['path'])
    for c in native['contrasts']:
        if c['classification']=='unavailable' or c['contrast']['control'] not in ('matched_update','v0_live_C1','v0_live_C2'):
            continue
        v=c['metrics']['RET-GS']
        add(f"comparator-{c['dataset']}-{c['contrast']['control']}",'Active inference testbed / PC context','measured',
            f"Paired RET-GS difference {v['estimate']:.6f}; r means {v['realization_estimates']}; preliminary label {c['classification']}",
            f"{c['dataset']}; 3 realizations × 5 orders at 1000 edits",c['contrast']['control'],
            'A comparison of the declared learned-reader and comparator packages',
            'Three-cluster labels do not establish familywise coverage; CounterFact locality loss prevents a positive label; not a factorial decomposition',report['analysis']['path'])
    learned=[r for r in report['groups'] if r['condition']=='R1_learned_ff']
    maxloss=max(v for r in learned for v in r['fidelity']['original']['max_positive_nll'])
    add('R1-fidelity','Heavy-tailed distributions / extremes','measured',
        f"45/45 learned-reader cells exceed mean KL .001; largest positive token ΔNLL {maxloss:.6f} nats",
        'Full validation: 245237 positions per cell, 3 datasets × 3 realizations × 5 orders','Original and own cap-off references, separately reported',
        'Retention can coexist with concentrated ordinary-text harm',
        'No heavy-tail family, power-law exponent, infinite variance, black-swan robustness or independent-token inference',report['analysis']['path'])
    for arm in ('ordinary','kappa02','kappa05','clip2'):
        values=[r for r in review['pilot']['rows'] if r['arm']==arm]
        add(f'kappa-{arm}','Heavy-tailed distributions / active-inference programme','development measured',
            f"RET-GS {statistics.mean(r['ret_gs'] for r in values):.6f}; positive-harm ES95 {statistics.mean(r['es95'] for r in values):.6f} nats",
            '3 training seeds × 3 development datasets; 32 windows / 4064 positions per dataset','Ordinary loss and clipped-surprisal control',
            'Loss-level robustness trade-off; both κ arms fail the declared retention/tail-separation rule',
            'DEC-054: preliminary hints, not coupled free energy, a coupled Markov blanket or the one-κ conjecture; not a confirmatory κ gain',
            'logs/r1_round22/ht3e-independent-review-v2.json')
    add('PC-v0','Predictive coding','pending','—','Exposed historical S5: zsRE1000 / CounterFact300; 3 realizations; preselected orders','Corrected SE-E vs SE-A; frozen regenerated ePC base',
        'Will test acquisition credit, retention, harm and cost','No measured efficacy result yet; historical defective-energy row and CPU smoke are not corrected experimental outcomes','docs/additional_work/PC-v0_report.md')
    add('PC-fixed-v5','Predictive coding','pending','—','Exposed R1 realization-0 streams; zsRE/CounterFact300, one order','Same selected BP-trained v5 reader/base; adjoint vs error acquisition',
        'Will test transfer of the acquisition-credit intervention','Not PC training of the reader, new confirmation, wholly BP-free computation or an expected-free-energy agent','docs/plan_from_saturday.md §4')
    add('PC-4-readiness','Predictive coding','implementation validated',
        f"{pc4['exact_prediction_count']} exact prediction checks; exact adjoint memory/counters; one real-base error-credit acquisition completed",
        'Saved v5 development checkpoint; four facts/eight prefixes plus one post-acquisition check; two-token acquisition','Original RevisionCap vs PCRevisionCap adjoint',
        'The seam executes with the original BP weights and preserves the adjoint path',
        'Not an efficacy comparison, speedup, GPU forecast or evidence of heavy-tail robustness','results/additional_work/PC-4/devcheckpoint.json')
    account=json.loads(Path(report['accounting']['path']).read_bytes())
    add('resources','All three: scope of evidence','measured',f"{report['complete_cells']} cells; {account['charged_hours']:.6f} charged process-hours",
        'Snapshot through queue cell '+str(report['through']),'Start/finish/driver receipts reconciled to block4',
        'Actual selected-snapshot computational spend','Not elapsed GPU hours; does not include later block5 or future PC work',report['accounting']['path'])
    add('unavailable','All three: scope of evidence','unavailable','—','All registered slots retained','S1_literal CounterFact and extension omitted under DEC-074b; MQuAKE comparator omission DEC-066',
        'Transparent incomplete scope','Absence is not zero effect; no outcome-based substitution','docs/R1_stage4_report_comparators.md')
    title='# Talk claim ledger v7 — active inference, predictive coding, and heavy-tailed distributions\n\n'
    title+='2026-09-26 preparation snapshot. Follows the [shared presentation brief](presentation/presentation_brief_2026-09-26.md). Every measured row names its population/control; pending PC rows remain empty. Experiments stop October 9 at 17:00 ET; presentation October 15. Three realizations and development training seeds are different replication units.\n\n'
    title+=table(['ID','theme','status','measured result','population','control','supports','does not support','source'],[list(r.values()) for r in rows])
    (ROOT/'docs/talk_claim_ledger_v7.md').write_text(title)
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--comparators')
    p.add_argument('--explanatory-only',action='store_true',help='Export PRES-2 drafts without regenerating measured ledger rows')
    p.add_argument('--output',required=True)
    a=p.parse_args()
    if a.explanatory_only:
        from aw.presentation_slides import export
        print(json.dumps(export(a.output)))
        return
    if not a.comparators:
        p.error('--comparators required unless --explanatory-only')
    out=Path(a.output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    figs=out/'figures'
    figs.mkdir()
    rows=ledger(a.comparators)
    diagrams(figs)
    copies=[]
    def copy(source,dest):
        source,dest=Path(source),Path(dest)
        shutil.copyfile(source,dest)
        copies.append(dict(source=dict(path=str(source.resolve()),sha256=sha(source)),export=dict(path=str(dest.resolve()),sha256=sha(dest))))
    copy(ROOT/'docs/presentation/deck_v3_outline.md',out/'outline.md')
    copy(ROOT/'docs/presentation/deck_v3_figure_pipeline.md',figs/'pipeline.md')
    copy(ROOT/'docs/talk_claim_ledger_v7.md',out/'claim-ledger-v7.md')
    sources={
        'triplet-behavior.png':ROOT/'logs/R1/reports/triplet/slide-figures/behavior-by-realization.png',
        'development-tail-survival.png':ROOT/'logs/r1_round35/ht6-final/tail-survival.png',
        'development-kappa-tradeoff.png':ROOT/'logs/r1_round37/presentation-figures-v2/kappa-tradeoff.png',
        'development-full-fidelity-and-tail.png':ROOT/'logs/r1_round37/presentation-figures-v2/full-fidelity-and-tail.png',
        'development-stress-trajectories.png':ROOT/'logs/r1_round37/presentation-figures-v2/stress-trajectories.png',
        'pc-v0-results-pending.png':ASSETS/'presentation-materials/figures/pc_v0/pending-20260926/efficacy-cost.png'}
    report=json.loads(Path(a.comparators).read_bytes())
    for ds in ('zsre','counterfact','mquake'):
        sources[f'{ds}-retention-harm.png']=ASSETS/f"presentation-materials/figures/comparators-{report['through']}/{ds}-retention-harm.png"
    for name,source in sources.items():
        copy(source,figs/name)
    bindings=[Path(__file__),Path(a.comparators),ROOT/'docs/presentation/presentation_brief_2026-09-26.md',
              ROOT/'logs/r1_round22/ht3e-independent-review-v2.json',ROOT/'results/additional_work/PC-4/devcheckpoint.json',
              ROOT.parent/'errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf',
              ROOT.parent/'errata/presentation_details/sattellite-schedule']
    manifest=dict(skeleton_only=True,task='PRES-1',claim_rows=len(rows),comparators_through=report['through'],
                  sources=[dict(path=str(x.resolve()),sha256=sha(x)) for x in bindings],copies=copies,
                  conceptual_figures=[dict(path=str(x),sha256=sha(x)) for x in figs.glob('*.svg')],
                  experimental_PC_results='pending; no smoke figure exported',gpu_seconds=0)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    log=ROOT/'logs/additional_work/round45/presentation-export.json'
    log.write_text(json.dumps(dict(output=str(out),manifest_sha256=sha(out/'manifest.json'),**manifest),indent=2)+'\n')
    print(json.dumps(dict(output=str(out),claims=len(rows),copied=len(copies))))


if __name__=='__main__':
    main()
