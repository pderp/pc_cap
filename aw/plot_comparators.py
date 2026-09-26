"""Render saved comparator statistics; no analyzer/model imports or new assays."""
import argparse
import json
import site
import statistics
from collections import defaultdict
from pathlib import Path

from aw.pc_v0_report import sha


def render(report_dir, output):
    packages=Path(__file__).resolve().parents[2]/'assets/envs/status-paper-20260911/lib/python3.12/site-packages'
    # Append existing plotting dependencies; preserve project NumPy/JAX.
    site.addsitedir(str(packages))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    report_path=Path(report_dir).resolve()/'report.json'
    report=json.loads(report_path.read_bytes())
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=True)
    conditions=sorted({r['condition'] for r in report['groups']})
    colors={c:plt.get_cmap('tab10')(i) for i,c in enumerate(conditions)}
    exports=[]
    for dataset in ('zsre','counterfact','mquake'):
        fig,axes=plt.subplots(1,2,figsize=(11,5.4),sharex=True)
        for ax,metric in zip(axes,('mean_kl','max_positive_nll')):
            points=defaultdict(list)
            ymax=0
            for condition in conditions:
                rows=[r for r in report['groups'] if r['dataset']==dataset and r['condition']==condition and r['full_order_grid']]
                if not rows:
                    continue
                xs=[statistics.mean(r['primary']['RET-GS']) for r in rows]
                ys=[statistics.mean(r['fidelity']['original'][metric]) if metric=='mean_kl' else max(r['fidelity']['original'][metric]) for r in rows]
                ax.scatter(xs,ys,label=condition,color=colors[condition],s=40,alpha=.8)
                for x,y,row in zip(xs,ys,rows):
                    points[x,y].append(row['realization'])
                    ymax=max(ymax,y)
            for (x,y),realizations in points.items():
                label=f'{len(realizations)} overlapping points' if len(realizations)>1 else f'r{realizations[0]}'
                offset=((5,4),(-15,4),(5,-10))[realizations[0]%3] if len(realizations)==1 else (7,12)
                ax.annotate(label,(x,y),xytext=offset,textcoords='offset points',fontsize=7)
            ax.set_xlabel('RET-GS: paraphrase retention')
            ax.set_xlim(-.025,1.05)
            if metric=='mean_kl':
                ax.set_yscale('symlog',linthresh=.0001)
                ax.set_ylim(0,max(.003,ymax*2.5))
                ax.axhline(.001,color='grey',linestyle=':',label='KL benchmark')
                ax.set_ylabel('Mean KL to original (nats; symlog)')
            else:
                ax.set_ylim(0,max(1,ymax*1.23))
                ax.set_ylabel('Largest positive token ΔNLL (nats)\nacross the five orders')
        handles,labels=axes[0].get_legend_handles_labels()
        fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=8)
        fig.suptitle(f'{dataset}: retention and harm — {report["through"]}-cell snapshot')
        fig.text(.5,.205,'Realization points: retention and KL average five orders; ΔNLL uses the maximum over five orders.',ha='center',fontsize=8)
        fig.text(.5,.174,'Coincident points remain at their measured coordinates; no confidence intervals.' + (' MQuAKE: 300 edits, descriptive.' if dataset=='mquake' else ''),ha='center',fontsize=8)
        fig.tight_layout(rect=(0,.235,1,.95))
        for extension in ('png','pdf','svg'):
            target=output/f'{dataset}-retention-harm.{extension}'
            fig.savefig(target,dpi=150)
            exports.append(dict(path=str(target),sha256=sha(target)))
        plt.close(fig)
    (output/'manifest.json').write_text(json.dumps(dict(source=dict(path=str(report_path),sha256=sha(report_path)),producer=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),exports=exports),indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-dir',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    render(args.report_dir,args.output)


if __name__=='__main__':
    main()
