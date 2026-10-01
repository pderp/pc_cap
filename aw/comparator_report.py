"""R1-D14e: registered analysis at the 225-cell boundary or DEC-074b halt.

CPU/read-only inputs. New output directory per snapshot; the readable document
may be refreshed. No operational queue action and no experimental rescoring.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from contextlib import contextmanager
from pathlib import Path

from scripts import ht8_fidelity_watch as watch
from scripts import r1_49g_analyze as native
from scripts import r1_77_queue as queue
from scripts import r1_d14_report as formatter

from aw.pc_v0_report import sha, table

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT/'manifests/revision_v1/run_matrix_final.json'
RECEIPTS = ROOT/'logs/R1/final_queue'


def save(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def csv_save(path, rows):
    if not rows:
        return
    with Path(path).open('x', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in rows)


@contextmanager
def scoped_loader(selected):
    old=native.old.load_cell
    def load(cell, files, scope):
        if cell['cell_id'] in selected:
            return old(cell,files,scope)
        value=old(dict(cell,result_dir=None),files,scope)
        value['snapshot_exclusion']='outside selected boundary; not a claim that a live result is absent'
        return value
    native.old.load_cell=load
    try:
        yield
    finally:
        native.old.load_cell=old


def accounting(cells):
    rows,bindings=[],{}
    matrix_sha=sha(MATRIX)
    for cell in cells:
        cost=queue.charged_cost(cell,queue.cell_cost(cell['result_dir']),RECEIPTS,matrix_sha)
        failures=[]
        missing=[]
        for rec in cost['process_receipts']:
            path=Path(rec['path'])
            finish=json.loads(path.read_bytes())
            if sha(path)!=rec['sha256']:
                raise ValueError('finish receipt changed')
            start=path.with_name('start.json')
            start_value=json.loads(start.read_bytes())
            recipe=start_value['recipe']
            if recipe['sha256']!=cell['manifest_sha256'] or sha(recipe['path'])!=recipe['sha256']:
                raise ValueError('process recipe differs')
            for p in (path,start,Path(recipe['path'])):
                bindings[str(p)]=sha(p)
            decision=path.with_name('decision.json')
            if decision.exists():
                dec=json.loads(decision.read_bytes())
                if dec['finish_sha256']!=rec['sha256']:
                    raise ValueError('parent decision differs')
                bindings[str(decision)]=sha(decision)
            else:
                missing.append(str(decision))
            if finish['exit_code']!=0 or finish.get('failure_class'):
                failures.append(dict(exit_code=finish['exit_code'],failure_class=finish.get('failure_class')))
        for attempt in cost['attempts']:
            if sha(attempt['path'])!=attempt['sha256']:
                raise ValueError('driver receipt changed')
            bindings[attempt['path']]=attempt['sha256']
        covered=sum(r['wall_seconds'] for r in cost['process_receipts'])
        rows.append(dict(cell_id=cell['cell_id'],condition=cell['condition'],dataset=cell['dataset'],
                         realization=cell['realization'],order=cell['order'],block=cell['block_number'],
                         charged_seconds=cost['known_attempt_wall_seconds'],process_seconds=covered,
                         uncovered_driver_seconds=max(0,cost['known_attempt_wall_seconds']-covered),
                         process_attempts=len(cost['process_receipts']),retries=max(0,len(cost['process_receipts'])-1),
                         failures=failures,unknown_attempts=cost['unknown_attempts'],missing_parent_decisions=missing))
    old_path=ROOT/'logs/R1/operator_reports/20260925-block4-try1/report.json'
    old=json.loads(old_path.read_bytes())
    old_rows={r['cell_id']:r for r in old['cost_ledger']['rows']}
    for row in rows:
        if row['block']<=4 and not math.isclose(row['charged_seconds'],old_rows[row['cell_id']]['charged_seconds'],abs_tol=1e-7):
            raise ValueError('block-4 historical charge changed')
    bindings[str(old_path)]=sha(old_path)
    return dict(rows=rows,charged_hours=sum(r['charged_seconds'] for r in rows)/3600,
                failures=sum(len(r['failures']) for r in rows),retries=sum(r['retries'] for r in rows),
                unknown_attempts=sum(len(r['unknown_attempts']) for r in rows),
                missing_parent_decisions=sum(len(r['missing_parent_decisions']) for r in rows),sources_sha256=bindings)


def analyze(output, through):
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    matrix=json.loads(MATRIX.read_bytes())
    cells=native.old.all_cells(matrix)[:through]
    selected={c['cell_id'] for c in cells}
    if len(selected)!=through:
        raise ValueError('boundary cell inventory differs')
    with scoped_loader(selected):
        report=native.run(MATRIX,output/'analysis-native')
    report['snapshot_scope']=dict(through=through,included_cell_ids=sorted(selected),decision='DEC-074b',
                                  interpretation='Results beyond this fixed boundary are outside this snapshot, not observed missing outcomes.')
    report['analysis_source_sha256']['aw/comparator_report.py']=sha(__file__)
    report['analysis_source_sha256']['aw/pc_v0_report.py']=sha(ROOT/'aw/pc_v0_report.py')
    save(output/'analysis.json',report)
    # A real historical prefix, with no filtered or fabricated watch events.
    raw=(ROOT/'results/R1/fidelity_watch/observations.jsonl').read_bytes()
    if not raw.endswith(b'\n'):
        raise ValueError('torn live watch read; retry with a fresh snapshot path')
    lines=raw.splitlines(keepends=True)
    expected={watch.full.digest(dict(mode='stage4_sealed_cell',recipe_sha256=c['manifest_sha256'],cell={k:c[k] for k in native.old.COORDS})) for c in cells}
    positions=[i for i,line in enumerate(lines) if json.loads(line)['observation']['cell_id'] in expected]
    prefix=b''.join(lines[:max(positions)+1]) if positions else b''
    events=[json.loads(line) for line in prefix.splitlines()]
    watch.replay(events)
    matrix_ids={watch.full.digest(dict(mode='stage4_sealed_cell',recipe_sha256=c['manifest_sha256'],cell={k:c[k] for k in native.old.COORDS})) for c in native.old.all_cells(matrix)}
    if any(e['observation']['cell_id'] in matrix_ids-expected for e in events):
        raise ValueError('watch boundary interleaves excluded cells; explicit scoped watch handling needed')
    (output/'watch-prefix.jsonl').write_bytes(prefix)
    account=accounting(cells)
    save(output/'accounting.json',account)
    csv_save(output/'accounting.csv',account['rows'])
    formatter.run(output/'analysis.json',output/'appendix',journal=output/'watch-prefix.jsonl')
    print(json.dumps(dict(through=through,complete=sum(c['artifact_complete'] for c in report['cells']),charged_hours=account['charged_hours'])),flush=True)


def groups(report):
    grouped={}
    for index,c in enumerate(report['cells']):
        if not c['artifact_complete']:
            continue
        coord=c['cell']
        grouped.setdefault((coord['dataset'],coord['condition'],coord['realization']),[]).append((index,c))
    result=[]
    for (ds,cond,r),values in sorted(grouped.items()):
        values.sort(key=lambda x:x[1]['cell']['order'])
        n=300 if ds=='mquake' else 1000
        cps=[v['checkpoints'][str(n)] for _,v in values]
        f=[c['secondary']['full_validation'] for c in cps]
        full=[v['cell']['order'] for _,v in values]==list(range(100,105))
        result.append(dict(dataset=ds,condition=cond,realization=r,checkpoint=n,complete_orders=len(values),full_order_grid=full,
                           primary={m:[c['primary'][m]['value'] for c in cps] for m in ('ES','RET-ES','RET-GS','LS')},
                           fidelity={ref:{'mean_kl':[x['references'][ref]['kl']['mean_signed'] for x in f],
                                          'mean_signed_nll':[x['references'][ref]['loss']['mean_signed'] for x in f],
                                          'max_positive_nll':[x['references'][ref]['loss']['maximum_positive'] for x in f],
                                          'half_kl_positions':[x['concentration']['references'][ref]['kl_positions']['minimum_count_for_half_mass'] for x in f]}
                                     for ref in ('original','capoff')},
                           benchmark_passes=sum(v['cap_fidelity_benchmark']['passes'] is True for _,v in values),
                           near_miss=[c['secondary']['near_miss_bounded']['value'] for c in cps],
                           revision_semantic=[c['secondary']['revision_semantic']['value'] for c in cps],
                           source_pointers=[f'/cells/{i}/checkpoints/{n}' for i,_ in values]))
    return result


def unavailable_reason(dataset, control, through):
    if dataset=='mquake':
        if control in ('R1_nonlearned','v0_stable'):
            return 'MQuAKE ends at 300; registered 1000-edit contrast unavailable (DEC-066); no substitution.'
        return 'MQuAKE comparator prospectively omitted under DEC-066 (zero calibrated radius); retained as unavailable.'
    if control=='S1_literal' and dataset=='counterfact':
        return 'Not run under DEC-074b: stop at 270 excludes S1_literal CounterFact.'
    if through==225 and control in ('S1_LM','S1_literal'):
        return 'Outside the block-4 snapshot; included in the planned 270-cell halt, pending reconciliation.'
    return 'Selected boundary has incomplete or unadmitted paired cells; inspect native inventory.'


def summarize(output, document, previous=None):
    output,document=Path(output).resolve(),Path(document).resolve()
    report=json.loads((output/'analysis.json').read_bytes())
    through=report['snapshot_scope']['through']
    account=json.loads((output/'accounting.json').read_bytes())
    rows=groups(report)
    unavailable=[]
    for c in report['contrasts']:
        if c['classification']=='unavailable':
            unavailable.append(dict(dataset=c['dataset'],contrast=c['contrast']['id'],
                                    reason=unavailable_reason(c['dataset'],c['contrast']['control'],through)))
    for ds in ('zsre','counterfact','mquake'):
        unavailable.append(dict(dataset=ds,contrast='historical-v2 extension (secondary)',reason='Optional 45-cell block 6 not run under DEC-074b; outside the 63 primary metric slots.'))
    value=dict(through=through,complete_cells=sum(c['artifact_complete'] for c in report['cells']),groups=rows,
               unavailable=unavailable,analysis=dict(path=str(output/'analysis.json'),sha256=sha(output/'analysis.json')),
               accounting=dict(path=str(output/'accounting.json'),sha256=sha(output/'accounting.json')),
               themes='Active inference programme; BP reader controls for PC credit study; distributional harm rather than a heavy-tail-family claim.')
    if previous:
        old=json.loads(Path(previous).read_bytes())
        old_keys={(r['dataset'],r['condition'],r['realization']) for r in old['groups']}
        value['changes']=dict(previous=dict(path=str(Path(previous).resolve()),sha256=sha(previous)),
                              prior_complete_cells=old['complete_cells'],new_complete_cells=value['complete_cells']-old['complete_cells'],
                              added_groups=[{k:r[k] for k in ('dataset','condition','realization')} for r in rows if (r['dataset'],r['condition'],r['realization']) not in old_keys])
    save(output/'report.json',value)
    csv_save(output/'realizations.csv',rows)
    csv_save(output/'unavailable.csv',unavailable)
    link='../'+str(output.relative_to(ROOT))
    text=f'# R1 Stage 4: comparator snapshot through queue cell {through}\n\n'
    text+=f"**{value['complete_cells']} completed cells** in this snapshot. Read-only registered D.5 analysis, with the original 63 primary metric slots retained. Later live results are outside this snapshot.\n\n"
    text+='Presentation framing: active inference supplies the programme, the present feedforward/BP reader supplies controlled evidence, and the PC credit experiment is a separate pending test. Heavy-tailed-distribution questions motivate measuring concentrated harm; these data do not establish a power-law tail or a complete active-inference agent.\n\n'
    text+='## Every realization\n\nEach displayed mean averages five orders within one realization. Incomplete order groups remain unavailable in this summary; the appendix retains their observed values. zsRE/CounterFact end at 1000 edits; MQuAKE at 300 is descriptive.\n\n'
    def avg(r,k):
        return statistics.mean(r['primary'][k]) if r['full_order_grid'] else None
    text+=table(['Dataset','condition','r','orders','ES','RET-ES','RET-GS','LS'],[[r['dataset'],r['condition'],r['realization'],r['complete_orders'],*[avg(r,k) for k in ('ES','RET-ES','RET-GS','LS')]] for r in rows])
    text+='## Registered paired contrasts\n\nEffects precede preliminary labels. Three realization clusters determine uncertainty; five orders are not five independent populations. The registered range interval does not establish 95% familywise coverage. Adjacent pointwise t sensitivity uses df=2 and an unverified normal/iid realization assumption; neither it nor a fidelity breach changes the classifier.\n\n'
    comparisons=[]
    for c in report['contrasts']:
        for metric,v in c['metrics'].items():
            if v['estimate'] is None:
                continue
            b,t=v['adjusted_interval'],v['preliminary']['t_sensitivity']
            comparisons.append([c['dataset'],c['contrast']['id'],metric,v['estimate'],v['realization_estimates'],f"[{b['lower']:.5g}, {b['upper']:.5g}]",f"[{t['lower']:.5g}, {t['upper']:.5g}]",c['classification']])
    text+=table(['Dataset','contrast','metric','difference','r0/r1/r2','registered range','t sensitivity','preliminary class'],comparisons)
    text+='## Fidelity and concentration\n\nBoth original and own-cap-off references are retained. They need not agree for continued-base controls. Means below average five cell means; maximum is the largest observed positive ΔNLL in that group. Half-KL counts retain all five order values. A zero total KL has undefined concentration, not concentration zero. See the appendix for quantiles, exceedances, expected shortfall, zero atoms, near miss and revision endpoints.\n\n'
    fr=[]
    for r in rows:
        for ref,f in r['fidelity'].items():
            fr.append([r['dataset'],r['condition'],r['realization'],ref,statistics.mean(f['mean_kl']),statistics.mean(f['mean_signed_nll']),max(f['max_positive_nll']),f['half_kl_positions'],f"{r['benchmark_passes']}/{r['complete_orders']}"])
    text+=table(['Dataset','condition','r','reference','mean KL','signed ΔNLL','max positive ΔNLL','positions for half KL','joint benchmark passes'],fr)
    from aw.report_limitations import PARAGRAPH
    text+='## Missing contrasts and execution accounting\n\n' + PARAGRAPH + '\n\n'
    text+=table(['Dataset','contrast','reason'],[[r['dataset'],r['contrast'],r['reason']] for r in unavailable])
    text+=f"Selected inventory: **{account['charged_hours']:.6f} charged process-hours**, {account['failures']} failed processes, {account['retries']} retries, {account['unknown_attempts']} unknown attempts. Covered driver cost is not counted twice. Process-hours can overlap across workers and are not elapsed GPU hours. {account['missing_parent_decisions']} missing parent decisions remain disclosed (the known Q21 interruption for the current snapshot). The selected inventory agrees with historical block-4 charges.\n\n"
    text+='The native global accounting adapter is explicitly unavailable because its current whole-queue replay would differ from this historical boundary. The separate selected-process inventory above is verified from enclosing start/finish/driver receipts. No operational record is manufactured or modified.\n\n'
    text+='S1_LM means a base continued on ordinary OpenWebText with a stable cap; S1_literal is a self-distillation negative control. Neither is direct fine-tuning on the factual edit stream, and neither is an exact-v5-compute-matched control. v0_live and matched-update controls test their declared packages; differences do not isolate every ingredient of the learned reader.\n\n'
    if previous:
        text+='## Changes since the earlier snapshot\n\n'+json.dumps(value['changes'],indent=2)+'\n\n'
    text+=f"[All native tables]({link}/appendix/report.md), [analysis/source identities]({link}/analysis.json), [selected execution inventory]({link}/accounting.json), [unavailable inventory]({link}/unavailable.csv). Run `python -m aw.comparator_report analyze --through 270 --output NEW_DIRECTORY` after the halt, followed by `publish --previous {output}/report.json` and `plot`; keep this 225-cell snapshot unchanged.\n"
    (output/'report.md').write_text(text)
    document.parent.mkdir(parents=True,exist_ok=True)
    document.write_text(text)
    save(output/'publication.json',dict(document=str(document),sha256=sha(document)))
    print(json.dumps(dict(groups=len(rows),available_contrasts=sum(c['classification']!='unavailable' for c in report['contrasts']),complete=value['complete_cells'])),flush=True)
    return value


def plot(output, figures):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output,figures=Path(output).resolve(),Path(figures).resolve()
    figures.mkdir(parents=True,exist_ok=False)
    report=json.loads((output/'report.json').read_bytes())
    conditions=sorted({r['condition'] for r in report['groups']})
    colors={c:plt.get_cmap('tab10')(i) for i,c in enumerate(conditions)}
    exports=[]
    for ds in ('zsre','counterfact','mquake'):
        fig,axes=plt.subplots(1,2,figsize=(11,5),sharex=True)
        for condition in conditions:
            rows=[r for r in report['groups'] if r['dataset']==ds and r['condition']==condition and r['full_order_grid']]
            if not rows:
                continue
            x=[statistics.mean(r['primary']['RET-GS']) for r in rows]
            for ax,metric in zip(axes,('mean_kl','max_positive_nll')):
                y=[statistics.mean(r['fidelity']['original'][metric]) if metric=='mean_kl' else max(r['fidelity']['original'][metric]) for r in rows]
                ax.scatter(x,y,label=condition,color=colors[condition],s=38,alpha=.85)
                for a,b,r in zip(x,y,rows):
                    ax.annotate(f"r{r['realization']}",(a,b),xytext=(3,3),textcoords='offset points',fontsize=7)
        axes[0].set_ylabel('Mean KL to original (nats; symlog)')
        axes[1].set_ylabel('Largest positive token ΔNLL (nats)')
        axes[0].set_yscale('symlog',linthresh=.0001)
        axes[0].axhline(.001,color='grey',linestyle=':',label='KL benchmark')
        for ax in axes:
            ax.set_xlabel('RET-GS: paraphrase retention')
            ax.set_xlim(-.04,1.04)
        handles,labels=axes[0].get_legend_handles_labels()
        fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=8)
        fig.suptitle(f"{ds}: retention and harm — {report['through']}-cell snapshot")
        fig.text(.5,.20,'Each point is one realization: mean of five orders; no token-level confidence intervals.',ha='center',fontsize=8)
        if ds=='mquake':
            fig.text(.5,.16,'300 edits, descriptive; later comparator arms were prospectively omitted.',ha='center',fontsize=8)
        fig.tight_layout(rect=(0,.24,1,.94))
        for ext in ('png','pdf','svg'):
            p=figures/f'{ds}-retention-harm.{ext}'
            fig.savefig(p,dpi=150)
            exports.append(dict(path=str(p),sha256=sha(p)))
        plt.close(fig)
    save(figures/'manifest.json',dict(source=dict(path=str(output/'report.json'),sha256=sha(output/'report.json')),producer=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),exports=exports))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('analyze','publish','plot','limitations'))
    p.add_argument('--through',type=int,choices=(225,270),default=225)
    p.add_argument('--output',required=True)
    p.add_argument('--document',default=str(ROOT/'docs/R1_stage4_report_comparators.md'))
    p.add_argument('--previous')
    p.add_argument('--figures')
    a=p.parse_args()
    if a.command=='limitations':
        from aw.report_limitations import refresh
        refresh(a.document, '## Missing contrasts and execution accounting')
        refresh(Path(a.output) / 'report.md', '## Missing contrasts and execution accounting')
        (Path(a.output) / 'publication.json').write_text(json.dumps(dict(document=str(Path(a.document).resolve()), sha256=sha(a.document)), indent=2) + '\n')
    elif a.command=='analyze':
        analyze(a.output,a.through)
    elif a.command=='publish':
        summarize(a.output,a.document,a.previous)
    else:
        plot(a.output,a.figures)


if __name__=='__main__':
    main()
