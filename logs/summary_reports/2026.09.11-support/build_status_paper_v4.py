"""Render the dated research paper from an immutable, local evidence snapshot.

CPU-only publishing code; imports neither pccap nor JAX. Destinations must be new.
Dependencies: reportlab, matplotlib, numpy. See README.md for the exact environment.
"""

import argparse
import hashlib
import io
import json
import os
import re
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

os.environ.setdefault('MPLCONFIGDIR', '/home/derp/cap/assets/tmp/status-paper-mpl')
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Image, Paragraph, Spacer, Table, TableStyle

NAVY = '#18374C'
TEAL = '#117C80'
RUST = '#B85434'
GOLD = '#AE8026'
GRAY = '#637483'
LIGHT = '#EDF3F5'
ARM_COLORS = {'C0': GRAY, 'C1': '#508AB1', 'C2': TEAL, 'CR': GOLD, 'CO': '#47566C', 'B0': '#AAB2BA', 'B1': '#BA735C', 'B3': RUST}
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 11,
    'axes.labelsize': 10, 'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#B3BFC6', 'text.color': NAVY, 'axes.labelcolor': NAVY,
    'xtick.color': GRAY, 'ytick.color': GRAY, 'figure.facecolor': 'white',
    'pdf.fonttype': 42, 'svg.fonttype': 'none', 'savefig.facecolor': 'white',
})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('evidence', type=Path)
    ap.add_argument('output_directory', type=Path)
    args = ap.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=False)
    out = args.output_directory
    data = json.loads(args.evidence.read_text())
    def source(path):
        return data['sources'][path]['content']
    def metrics(path):
        return {k: v['value'] for k, v in source(path)['metrics'].items()}
    frozen = source('manifests/frozen.json')
    p1 = metrics('git:25c988b:results/S1/P1_epc.json')
    p6 = metrics('results/S1/P6_epc.json')
    p4 = metrics('results/S1/P4_gram.json')
    reg = source('results/REG/epc-50m/summary.json')
    dev = dict(source('results/S2/throughput_v2.json')['runs'])
    dev.update(source('results/S2/throughput_v2_baselines.json')['runs'])
    gram = source('results/S3/grammar_dev_matrix.json')['runs']
    fixture = source('results/S3/fixture/summary.json')['variants']['useful_sharing']
    replay = source('results/S2/grace_jax/gradient_localization/reduction_replay_candidate.json')['cases']
    projection = source('results/S2/projection.json')
    selected = next(r for r in projection['table'] if all(r[k] == projection['selected'][k] for k in ('zsre', 'counterfact', 'grammar')))
    s4h = selected['seconds'] / 3600
    b4h = sum(v for k, v in selected['parts'].items() if k.startswith('B4/')) / 3600
    s5h = source('results/S5/projection.json')['total_local_hours']
    cutoff = datetime.fromisoformat(data['capture_finished_utc']).astimezone(ZoneInfo('America/New_York'))
    cutoff_text = cutoff.strftime('%d September %Y, %H:%M:%S EDT')
    progress = data['progress']
    assert len(data['runs']) == 5 and {r['job']['arm'] for r in data['runs']} == {'C0'}
    assert {r['job']['realization'] for r in data['runs']} == {0}
    figures = {}
    def save(fig, name):
        png, pdf = out / (name + '.png'), out / (name + '.pdf')
        fig.savefig(png, dpi=240, bbox_inches='tight', pad_inches=0.12)
        fig.savefig(pdf, bbox_inches='tight', pad_inches=0.12)
        plt.close(fig)
        figures[name] = png

    # Figure 1: a schematic, not an empirical result.
    fig, ax = plt.subplots(figsize=(7.1, 3.35))
    ax.set(xlim=(0, 10), ylim=(0, 4)); ax.axis('off')
    def box(x, y, w, h, text, fc=LIGHT, ec=NAVY, fs=10):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.07,rounding_size=0.08', facecolor=fc, edgecolor=ec, linewidth=1))
        ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=fs)
    def arrow(a,b,color=NAVY):
        ax.add_patch(FancyArrowPatch(a,b, arrowstyle='-|>', mutation_scale=11, color=color, linewidth=1.2))
    box(.05, 2.3, 1.05, .8, 'Prompt\ntokens')
    for i,x in enumerate((1.7,4.0,6.3)):
        box(x,2.3,1.55,.8,f'Blocks\n{4*i+1}–{4*i+4}')
        box(x,1.05,1.55,.7,f'Bank {i+1}\nkey + correction',fc='#DDEEEF',ec=TEAL,fs=9)
        arrow((x+.77,2.28),(x+.77,1.8),TEAL)
        arrow((x+1.38,1.8),(x+1.38,2.28),TEAL)
    box(8.5,2.3,1.35,.8,'Next-token\nanswer',fs=9)
    for a,b in [((1.15,2.7),(1.63,2.7)),((3.3,2.7),(3.92,2.7)),((5.6,2.7),(6.22,2.7)),((7.9,2.7),(8.42,2.7))]:arrow(a,b)
    ax.text(4.8,3.6,'Frozen GPT-2: 12 blocks, width 768',ha='center',fontsize=12,weight='bold')
    ax.text(4.8,.53,'Learning: trial writes → measured loss change → choose delivery site',ha='center',fontsize=10,color=TEAL)
    ax.text(4.8,.05,'Prediction: retrieve within a calibrated radius; add a stored correction',ha='center',fontsize=9.5)
    save(fig,'fig01_apparatus')

    # Figure 2: fixed-iteration errors on the actual regenerated checkpoint.
    fig, axs = plt.subplots(1,2,figsize=(7.15,3.15), layout='constrained')
    ax=axs[0]
    vals=[p6['r_8_mean'],p6['r_64_mean']]
    ax.bar(['8 iterations','64 iterations'],vals,color=[TEAL,GRAY],width=.55)
    ax.set_yscale('log');ax.set_ylim(.0005,1);ax.set_ylabel('Mean residual ratio (log scale)')
    ax.axhline(.001,color=RUST,ls='--',lw=1)
    ax.text(-.38,.0013,'Per-prompt criterion: 0.001',fontsize=8.2,color=RUST)
    for i,v in enumerate(vals): ax.text(i,v*1.16,f'{v:.3f}',ha='center',fontsize=10)
    ax.set_title('A  Error inference remains unsettled',loc='left')
    ax=axs[1]; x=np.arange(3);w=.34
    for offset,t,color in [(-w/2,8,TEAL),(w/2,64,GRAY)]:
        vv=[p6[f'cos_bank{b}_cos_e{t}_negadj'] for b in (1,2,3)]
        ax.bar(x+offset,vv,w,color=color,label=f'{t} iterations')
    ax.set_xticks(x,['Bank 1','Bank 2','Bank 3']);ax.set_ylim(0,1.17)
    ax.set_ylabel('Cosine with negative adjoint');ax.legend(frameon=False,fontsize=8,loc='upper left')
    ax.set_title('B  Alignment depends on depth and T',loc='left')
    save(fig,'fig02_epc_credit')

    # Figure 3: separate constructed and learned synthetic test beds.
    fig,axs=plt.subplots(1,2,figsize=(7.15,3.1),layout='constrained')
    ax=axs[0]; arms=['C0','C1','C2','CR','CO'];x=np.arange(len(arms));w=.37
    a=ax.bar(x-w/2,[fixture[k]['recovery_rate']*100 for k in arms],w,color=TEAL,label='Recovery')
    b=ax.bar(x+w/2,[fixture[k]['delivery']['precision']['value']*100 for k in arms],w,color=GRAY,label='Delivery precision')
    ax.set_xticks(x,arms);ax.set_ylim(0,125);ax.set_yticks(range(0,101,20));ax.set_ylabel('Percent');ax.legend(frameon=False,fontsize=8,loc='upper left')
    ax.set_title('A  Constructed useful-sharing fixture',loc='left',fontsize=10)
    ax=axs[1];arms=['C0','C1','C2','CR'];x=np.arange(4)
    for off,key,label,color in [(-w/2,'ret_es_end','Retained exact edit',TEAL),(w/2,'ret_gs_end','Retained paraphrase',GOLD)]:
        means=[100*np.mean([gram[f'{a}/perm{p}']['metrics'][key] for p in (0,1)]) for a in arms]
        ax.bar(x+off,means,w,color=color,label=label)
        for i,a in enumerate(arms):
            vals=[100*gram[f'{a}/perm{p}']['metrics'][key] for p in (0,1)]
            ax.scatter([i+off-.025,i+off+.025],vals,s=12,c=NAVY,zorder=3)
    ax.set_xticks(x,arms);ax.set_ylim(0,125);ax.set_yticks(range(0,101,20));ax.set_ylabel('Accuracy (%)');ax.legend(frameon=False,fontsize=8,loc='upper left')
    ax.set_title('B  Learned replacement grammar',loc='left',fontsize=10)
    save(fig,'fig03_synthetic')

    # Figure 4: no inferential error bars for a single development order.
    fig,ax=plt.subplots(figsize=(7.15,3.55),layout='constrained')
    arms=['C0','C1','C2','CR','B0','B1','B3']; x=np.arange(len(arms));w=.25
    for off,key,label,color in [(-w,'es_immediate','Immediate edit (ES)',TEAL),(0,'ret_gs_end','Retained paraphrase (RET-GS)',GOLD),(w,'ls_complete_answer_end','Locality (LS)',GRAY)]:
        vals=[100*dev[f'{a}/zsre']['metrics'][key] for a in arms]
        bars=ax.bar(x+off,vals,w,color=color,label=label)
        for bar,v in zip(bars,vals):ax.text(bar.get_x()+w/2,max(v,0)+1.5,f'{v:.0f}',ha='center',fontsize=7.8)
    ax.set_xticks(x,['C0\nlast bank','C1\nall banks','C2\nmeasured','CR\nlearned random','B0\nfrozen','B1\nLoRA','B3\nLoRA + replay'])
    ax.set_ylim(0,124);ax.set_yticks(range(0,101,20));ax.set_ylabel('Complete-answer accuracy / agreement (%)')
    ax.legend(frameon=False,ncol=3,fontsize=8,loc='upper left')
    ax.set_title('zsRE development: 100 edits per arm, one order',loc='left',pad=12)
    save(fig,'fig04_natural_language')

    # Figure 5: do not conflate projection capture and subspace overlap.
    fig,axs=plt.subplots(1,2,figsize=(7.15,3.5),layout='constrained')
    overlap=np.eye(3)
    overlap[0,1]=overlap[1,0]=p4['error_overlap_private_shared1_mean']
    overlap[0,2]=overlap[2,0]=p4['error_overlap_private_shared2_mean']
    overlap[1,2]=overlap[2,1]=p4['error_overlap_shared1_shared2_mean']
    ax=axs[0];im=ax.imshow(overlap,cmap='Blues',vmin=0,vmax=1)
    ax.set_xticks(range(3),['Private','Shared 1','Shared 2'],rotation=25,ha='right')
    ax.set_yticks(range(3),['Private','Shared 1','Shared 2'])
    for i in range(3):
        for j in range(3):ax.text(j,i,f'{overlap[i,j]:.3f}',ha='center',va='center',color='white' if overlap[i,j]>.6 else NAVY,fontsize=10)
    ax.set_title('A  Error-subspace overlap',loc='left')
    ax=axs[1];x=np.arange(2);w=.35
    same=[p4['heldout_transfer_private_mean'],p4['heldout_transfer_shared_mean']]
    cross=[p4['cross_capture_shared_basis_on_private_only_flip_mean'],p4['cross_capture_private_basis_on_shared_only_flip_mean']]
    for off,vv,label,c in [(-w/2,same,'Matching basis',TEAL),(w/2,cross,'Other basis',GOLD)]:
        ax.bar(x+off,vv,w,label=label,color=c)
        for i,v in enumerate(vv):ax.text(i+off,v+.025,f'{v:.3f}',ha='center',fontsize=8)
    ax.set_xticks(x,['Private-only\nchange','Shared-only\nchange']);ax.set_ylim(0,1.27);ax.set_yticks(np.linspace(0,1,6))
    ax.set_ylabel('Held-out error projection capture');ax.legend(frameon=False,fontsize=8,loc='upper left')
    ax.set_title('B  Held-out mechanism changes',loc='left')
    save(fig,'fig05_mechanism')

    fig,ax=plt.subplots(figsize=(7.1,3.15),layout='constrained')
    x=np.arange(2);w=.32
    for off,key,label,c in [(-w/2,'native','Native backward reductions',RUST),(w/2,'head64_and_loss64','Float64 head + loss replay',TEAL)]:
        vv=[cse['jax_vs_backward_replays'][key]['relative_l2'] for cse in replay]
        ax.bar(x+off,vv,w,color=c,label=label)
        for i,v in enumerate(vv):ax.text(i+off,v*1.15,f'{v:.2e}',ha='center',fontsize=9)
    ax.set_yscale('log');ax.set_ylim(3e-6,7e-4);ax.set_xticks(x,['Fixed case 0','Fixed case 1'])
    ax.set_ylabel('Relative L2 gradient difference (log scale)')
    ax.legend(frameon=False,fontsize=9,loc='upper right')
    ax.set_title('GRACE diagnostic: compare the unchanged JAX gradient with reference replays',loc='left',fontsize=10)
    save(fig,'fig06_grace_numerics')

    fig,ax=plt.subplots(figsize=(7.1,2.8),layout='constrained')
    names=['S4 scope projection','S4 minus excluded B4*','S5 additional runs','REG-02 observed use']
    vals=[s4h,s4h-b4h,s5h,reg['gpu_seconds']/3600]
    ax.barh(range(4),vals,color=[GRAY,TEAL,TEAL,RUST],height=.54)
    for i,v in enumerate(vals):ax.text(v+.25,i,f'{v:.2f} h',va='center',fontsize=10)
    ax.vlines(27,-.45,1.45,color=NAVY,linestyle='--',linewidth=1.2)
    ax.vlines(18,1.57,2.43,color=NAVY,linestyle='--',linewidth=1.2)
    ax.text(27.25,.55,'S4 allowance\n27 h',fontsize=8,va='center')
    ax.text(18.25,2,'S5 allowance\n18 h',fontsize=8,va='center')
    ax.set_yticks(range(4),names);ax.invert_yaxis();ax.set_xlim(0,33)
    ax.set_xlabel('Local accelerator hours at provisional κ = 1')
    save(fig,'fig07_resources')

    fig,ax=plt.subplots(figsize=(7.1,3.45),layout='constrained')
    labels=['Foundation (S0–S2)','Screen / freeze (S3–S4)','Confirmation (S4)','Substrate / credit (S5)','Order effects (S7)','Final audit / report (S8)']
    windows=[(1,2),(2,3),(3,4),(3,4),(3,5),(4,5)]
    for i,(start,end) in enumerate(windows):
        ax.barh(i,end-start,left=start,height=.45,color='#D6E2E8',edgecolor=GRAY,lw=.6)
    ax.axvline(1+2/7,color=RUST,lw=1.5)
    ax.text(1+2/7+.045,-.45,'Day 3',color=RUST,fontsize=9)
    statuses=['Core apparatus ready; qualifications remain','Development screened; v2 frozen','Running: 5 / 210 jobs at cutoff','60 new jobs scheduled; SB reused','Inventory ready; reversals pending','Final reproduction and synthesis pending']
    for i,t in enumerate(statuses):ax.text(1.01,i+.36,t,fontsize=7.8,color=NAVY,va='top')
    ax.set_yticks(range(6),labels);ax.set_xticks([1.5,2.5,3.5,4.5],['Week 1','Week 2','Week 3','Week 4'])
    ax.set_xlim(1,5);ax.set_ylim(5.7,-.75);ax.set_xlabel('Original plan windows (not completion fractions)')
    save(fig,'fig08_timeline')

    # Additional descriptive property curve; no causal efficacy interpretation.
    p2=metrics('results/S1/P2_epc.json')
    fig,ax=plt.subplots(figsize=(7.1,2.65),layout='constrained')
    ax.plot(range(13),[p2[f'effective_rank_layer{i}'] for i in range(13)],color=TEAL,marker='o',lw=1.7,markersize=4)
    ax.set_xticks(range(13));ax.set_ylim(0,400)
    ax.set_xlabel('Recorded site: 0 = embedding; 1–12 = successive block outputs')
    ax.set_ylabel('Effective rank')
    ax.set_title('P2: regenerated ePC hidden-feature spectrum, 4,096 sampled positions',loc='left',fontsize=10)
    save(fig,'fig09_feature_rank')

    font_dir=Path(matplotlib.get_data_path())/'fonts/ttf'
    for name,file in [('Body','DejaVuSerif.ttf'),('Body-Bold','DejaVuSerif-Bold.ttf'),('Body-Italic','DejaVuSerif-Italic.ttf'),('Sans','DejaVuSans.ttf'),('Sans-Bold','DejaVuSans-Bold.ttf'),('Sans-Oblique','DejaVuSans-Oblique.ttf'),('Mono','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body-Italic',boldItalic='Body-Bold')
    pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Sans-Bold',italic='Sans-Oblique',boldItalic='Sans-Bold')
    styles={
        'body':ParagraphStyle('body',fontName='Body',fontSize=10.1,leading=14.1,spaceAfter=8,textColor=colors.HexColor(NAVY),alignment=TA_LEFT),
        'small':ParagraphStyle('small',fontName='Sans',fontSize=8.7,leading=12.2,spaceAfter=5,textColor=colors.HexColor(NAVY)),
        'tcap':ParagraphStyle('tcap',fontName='Sans',fontSize=8.5,leading=11.6,spaceBefore=2,spaceAfter=5,textColor=colors.HexColor(GRAY)),
        'caption':ParagraphStyle('caption',fontName='Sans',fontSize=8.5,leading=11.6,spaceBefore=5,spaceAfter=12,textColor=colors.HexColor(GRAY)),
        'h1':ParagraphStyle('h1',fontName='Sans-Bold',fontSize=17,leading=21,spaceAfter=14,textColor=colors.HexColor(NAVY)),
        'h2':ParagraphStyle('h2',fontName='Sans-Bold',fontSize=11.3,leading=15,spaceBefore=5,spaceAfter=7,textColor=colors.HexColor(TEAL)),
        'title':ParagraphStyle('title',fontName='Sans-Bold',fontSize=27,leading=33,spaceAfter=12,textColor=colors.HexColor(NAVY)),
        'subtitle':ParagraphStyle('subtitle',fontName='Sans',fontSize=12,leading=17,spaceAfter=14,textColor=colors.HexColor(TEAL)),
        'kicker':ParagraphStyle('kicker',fontName='Sans-Bold',fontSize=8.6,leading=12,spaceAfter=12,textColor=colors.HexColor(TEAL)),
        'cell':ParagraphStyle('cell',fontName='Sans',fontSize=8.8,leading=12,textColor=colors.HexColor(NAVY)),
        'cellhead':ParagraphStyle('cellhead',fontName='Sans-Bold',fontSize=8.6,leading=11.5,textColor=colors.white),
        'mono':ParagraphStyle('mono',fontName='Mono',fontSize=7,leading=9,spaceAfter=5,wordWrap='CJK',textColor=colors.HexColor(NAVY)),
    }
    width,height=A4
    usable=width-88
    pages=[]; manuscript=[]
    def page(title):
        story=[];pages.append((title,story));manuscript.append('\n\n# '+title+'\n');return story
    def p(story,text,style='body'):
        story.append(Paragraph(text,styles[style]));manuscript.append(re.sub('<[^>]+>','',text)+'\n')
    def h(story,text):p(story,text,'h2')
    table_titles=iter(['Experimental arms','Outcome measures','Frozen job schedule','Full P1 fidelity audit','CounterFact development','Partial C0 confirmation','Verification coverage','Risks and responsibilities','Remaining completion checks','Additional property diagnostics','Glossary'])
    table_count=0
    def table(story,headers,rows,widths):
        nonlocal table_count
        table_count+=1
        p(story,f'<b>Table {table_count}.</b> '+next(table_titles),'tcap')
        cells=[[Paragraph(escape(str(t)),styles['cellhead']) for t in headers]]
        cells += [[Paragraph(str(t),styles['cell']) for t in row] for row in rows]
        obj=Table(cells,colWidths=[usable*w/sum(widths) for w in widths],hAlign='LEFT')
        obj.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(NAVY)),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F0F5F6'),colors.white]),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),
            ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),
            ('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#BCD0D8')),
        ]));story.extend([obj,Spacer(1,10)])
        manuscript.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n')
        manuscript.extend('| '+' | '.join(re.sub('<[^>]+>','',str(c)) for c in row)+' |\n' for row in rows)
    def figure(story,name,caption,maxheight=245):
        im=Image(str(figures[name]));scale=min(usable/im.imageWidth,maxheight/im.imageHeight)
        im.drawWidth=im.imageWidth*scale;im.drawHeight=im.imageHeight*scale
        story.append(im);p(story,caption,'caption');manuscript.append('!['+caption+']('+name+'.png)\n')
    def callout(story,label,text):
        inner=Paragraph('<b>'+label+'</b><br/>'+text,styles['small'])
        box=Table([[inner]],colWidths=[usable]);box.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#E7F0F2')),('BOX',(0,0),(-1,-1),.7,colors.HexColor('#A9C4CD')),
            ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
            ('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),11),
        ]));story.extend([box,Spacer(1,12)]);manuscript.append('**'+label+'** '+text+'\n')

    s=page('Current research status')
    p(s,'PC_CAP  •  INTERIM RESEARCH PAPER  •  11 SEPTEMBER 2026','kicker')
    p(s,'Continual learning through<br/>predictive-coding caps','title')
    p(s,'Current evidence, confirmatory readiness, and the remaining research programme','subtitle')
    p(s,'pc_cap research project · Evidence synthesis prepared by Codex<br/>Source-of-truth plan: Goertzel &amp; Fable, revised 7 September 2026 [1].<br/><b>Evidence cutoff:</b> '+cutoff_text+' (16:39:45 UTC).','small')
    h(s,'Abstract')
    p(s,'This project studies whether a small, bounded correction memory can teach a frozen language model new answers while preserving unrelated behavior. The central hypothesis is that measuring where an intervention helps, then routing learning to that location, improves retention relative to simpler delivery rules at comparable cost. A second thread separates the effects of an error-based predictive-coding substrate from those of its credit signal. The JAX apparatus, controlled fixtures, regenerated substrate, and frozen comparison schedule are implemented. Regeneration processed 50.002 million tokens in 12.18 local GPU-hours; the full fidelity audit measured mean KL divergence of 2.923 × 10<super>−5</super> over 1,999,872 positions. Constructed examples validate useful routing, but short natural-language development runs do not demonstrate a routing advantage. At cutoff, five of 210 S4 jobs were complete, all C0 orders within one zsRE realization; the required C2 contrasts remain unmeasured. GRACE is excluded after its registration gate failed. A newly identified drift-evaluation sample mismatch requires lead review before plan-conformant drift claims. The project has reached confirmation early in its calendar, but a final scientific verdict and reliable resource forecast remain pending.')
    h(s,'For a reader new to the project')
    p(s,'Think of the base model as a reference book whose pages cannot be rewritten. The cap adds a limited set of notes that activate for relevant questions. The experiment asks both whether the notes last and where inside the model they should be applied. Remembering the exact question is easier than answering a rephrased question; the latter is the main test.')
    callout(s,'Present conclusion','The apparatus supports a controlled experiment. It has not yet established that measured routing, predictive-coding conversion, or error-based credit improves continual learning. Development findings and partial confirmation are reported separately throughout.')
    p(s,'Keywords: continual learning; activation memory; model editing; predictive coding; frozen transformers; paired experiments. This is an internal interim paper, not a peer-reviewed claim of efficacy.','small')

    s=page('1. Research question and experimental apparatus')
    p(s,'1. Research question and experimental apparatus','h1')
    p(s,'Learning one correction can damage another when both use the same internal mechanism. The original plan asks whether targeted delivery can reduce that interference while preserving useful sharing. It explicitly separates the location of a helpful write, the representation carrying it, and the rule that computes the write direction [1].')
    figure(s,'fig01_apparatus','Figure 1. Cap v0 on the frozen GPT-2 base. Banks attach after blocks 4, 8, and 12 (zero-based sites 3, 7, 11; the last before final layer normalization). Arrows show reads and additive writes; the drawing does not imply that every bank fires on every query [1,2].',205)
    table(s,['Arm','Delivery or learning rule','Role'],[
        ['C0','Last bank only; the entire cap byte budget is at that bank.','Simple late-correction comparator.'],
        ['C1','All three banks share the total write-step budget.','Main distributed-delivery comparator.'],
        ['C2','Probe each bank; select the greatest positive loss improvement; abstain if none helps.','Measured routing hypothesis.'],
        ['CR','Choose a bank randomly using probabilities fixed from development C2 deliveries.','Controls for where C2 tends to write.'],
        ['CO','Supplied correct site in constructed fixtures only.','Diagnostic oracle; no natural-language claim.'],
        ['B0 / B1 / B3','Frozen base / rank-8 low-rank adaptation (LoRA) / the same adapter plus replay.','Baseline context; B3 enters confirmation.'],
    ],[.6,2.9,1.6])
    p(s,'A slot stores an address, a correction, a radius and bounded metadata. Retrieval is gated by similarity; a miss leaves the base behavior intact. The base weights remain frozen during cap learning. Cap v0 is a PC-motivated activation memory: it does not itself run an autonomous predictive-coding inference process. JAX supplies CUDA execution; FabricPC and the sibling predictive-coding repository serve as read-only resources [1,2,14].')

    s=page('2. Frozen methods and decision criteria')
    p(s,'2. Frozen methods and decision criteria','h1')
    p(s,'The development phase chose settings before the confirmatory data were opened. The v2 manifest binds the code tree, environment lock, tokenizer, base checkpoints, data identities, random seeds, scope, budgets and analysis rules. It was frozen at 16:17:30 UTC on 11 September. The present paper reads saved run summaries and source code; it does not open sealed item manifests or tune on confirmation [2].')
    table(s,['Measure','Meaning and interpretation'],[
        ['ES / GS','Immediate complete-answer accuracy on the edited question / its paraphrases. Free generation must match an accepted complete answer.'],
        ['RET-ES / RET-GS','Accuracy after subsequent edits, on original questions / paraphrases. RET-GS is the primary endpoint; exact-edit retention is a companion.'],
        ['LS','Agreement with the cap-disabled base on unrelated complete answers. Agreement measures preservation, not factual correctness.'],
        ['LM drift','Perplexity ratio and mean loss change on held-out text. Ratio 1 means no measured drift on the evaluated sample; see the sample-size defect in Section 8.'],
    ],[1,4])
    p(s,'Each dataset uses three sampled stream realizations and five fixed orders per realization. The 15 orders are paired across arms, but they are <b>not 15 independent datasets</b>. Analysis resamples the three realization means, keeping all five orders together, using 10,000 bootstrap draws and two-sided 97.5% percentile intervals. This is a small-cluster uncertainty assessment [2,15].')
    callout(s,'What would count as support?','For both C2−C1 and C2−CR: the RET-GS point gain must be at least 2 percentage points and its interval lower bound above zero. The ES lower bound must exceed −2 points, and the LS lower bound −1 point. Incomplete pairs are not imputed. Other outcomes are classified as qualified, inconclusive or negative under the frozen policy [2,15].')
    table(s,['Scheduled work','Scope','Jobs'],[
        ['S4: C1, C2, CR, B3','zsRE 1,000 edits; CounterFact 300; 15 runs per arm/dataset.','120'],
        ['S4: C0','Initial 300 edits per natural-language stream/order.','30'],
        ['S4: grammar','C0/C1/C2/CR; eight tasks × 256 sequences/task; 15 runs.','60'],
        ['S5: SE-A and SE-E','Two natural-language datasets × 15 runs × two new arms.','60'],
    ],[1.5,3.2,.5])
    p(s,'The cap ceiling is 38,535,168 bytes (36.75 MiB), with 6,272 bytes per slot. Shared settings are A = 0.3, probe ε = 0.01, five rounds per target prefix, and edit-loss threshold 0.1 nats. Radii target ≤1% unrelated false firings. Matching total bytes does not match each bank’s capacity: interpret C0 versus distributed arms with that allocation difference and with C0’s shorter scope. Compute comparisons require measured update costs within 20%, or an explicit cost frontier [1,2].','small')

    s=page('3. Regenerated substrate: faithful, but not settled')
    p(s,'3. Regenerated substrate: faithful, but not settled','h1')
    p(s,'The unavailable inherited checkpoint was replaced by a new, documented run. REG-02 finished 9,766 steps on 50,001,920 tokens, using a settling schedule T = 1, 2, 4, 8, 16, 32, 64. It consumed 12.18 local GPU-hours; the terminal summary reports 7,447 MiB peak memory. This is a regenerated substrate, not a recovered copy of the earlier research artifact [3].')
    table(s,['Full P1 fidelity audit','Result','Interpretation'],[
        ['Prediction positions','1,999,872','Held-out WikiText-103 train sample H.'],
        ['Mean / 99th-percentile KL','2.923e−5 / 2.445e−4 nats','Mean is below the 1e−3 eligibility ceiling.'],
        ['Maximum finite KL / nonfinite positions','0.1161 / 0','A small average does not bound every token.'],
        ['Teacher–student argmax agreement','99.649%','Agreement, not answer accuracy.'],
        ['Teacher / student mean NLL','3.570225 / 3.569724 nats','Very similar predictive distributions.'],
    ],[1.8,1.5,2.3])
    figure(s,'fig02_epc_credit','Figure 2. Actual regenerated ePC checkpoint, 64 development prompts (32 per natural-language dataset). Residual bars are prompt means, with no confidence intervals. The dashed line is only one part of the per-prompt convergence test. Cosines compare errors with the negative adjoint; high alignment is not evidence of editing superiority [4].',220)
    p(s,'Eight-step credit is labeled <b>finite-iteration error credit</b>. Mean residual ratios are 0.404 at eight steps and 0.098 at 64; the maximum at 64 is 1.350. The declared settled criterion requires ≤0.001 for every prompt plus negligible final energy change. Mean energy falls by 2.423 nats, but settling is not established. Longer inference also reduces early-bank alignment with the adjoint in this diagnostic [4].')
    p(s,'The full P1 record is preserved in Git commit 25c988b. Its live filename later held a 199,680-position follow-up, with a similar mean KL of 2.875e−5. This paper preserves and cites both separately. The regenerated parameters moved only 4.460e−4 in relative norm, so fidelity eligibility should not be read as evidence of a better learning substrate [3,4].','small')

    s=page('4. Constructed and learned synthetic evidence')
    p(s,'4. Constructed and learned synthetic evidence','h1')
    p(s,'Two synthetic settings answer different questions. A constructed modular fixture has a known useful delivery site, making it suitable for checking the apparatus. A learned grammar has shared and private latent causes, so its internal organization must be measured rather than assumed. Both are development evidence [5,6].')
    figure(s,'fig03_synthetic','Figure 3. A: useful-sharing fixture, 180 items per arm (60 private, 60 shared, 60 mixed); precision is measured over deliveries. B: grammar development, one realization and two orders, each eight tasks × 16 items. Bars are order means; dots show the two observed values, not confidence intervals. The panels use different metrics and populations [5,6].',250)
    h(s,'Constructed fixture: delivery can matter when the site is known')
    p(s,'C2 and the oracle recover 180/180 items; C1 recovers 178/180, CR 170/180, and C0 46/180. C2 delivery precision is 87.9% and recall 89.4%, compared with C1 precision 48.1% and recall 100%. Recovery can therefore be perfect even when the measured delivery pattern is not identical to the oracle’s. The separate PC-1 controls recover 20/20 planted targets and 120/120 full-fixture cases, while a wrong router recovers only 1/30 in its negative control [5,11].')
    h(s,'Learned grammar: exact edits succeed; generalization is restricted')
    p(s,'Grammar RET-ES is 100% for C0 and C2, 70.3% for C1, and 91.4% for CR in both development orders. C2 RET-GS is 25.78% and 25.39%. No positive retrieval radius met the false-firing criterion, so the grammar uses exact keys. The report identifies these paraphrase scores as the base’s task-accuracy floor, not retrieval generalization. Locality is 100% on the tested prompts; the grammar drift ratio is a synthetic-domain diagnostic, not a WikiText language-model result [6].')
    p(s,'The replacement grammar is available in the v2 freeze but remains provisional under PA-2 until 11 September at 23:59 Eastern. It must retain replacement provenance if the inherited artifacts do not arrive. Synthetic results establish controlled feasibility; they do not by themselves establish that the same latent mechanisms or routing benefits exist in natural language [2,6].')

    s=page('5. Natural-language development: a mixed result')
    p(s,'5. Natural-language development: a mixed result','h1')
    p(s,'zsRE supplies question-answer edits; CounterFact supplies factual replacements and paraphrases. The revised throughput matrix evaluates 100 edits per arm and dataset in one development order. These runs selected and priced the experiment; they are not independent confirmation. Figure 4 uses the revised JSON records, including CR’s development-learned bank distribution [7].')
    figure(s,'fig04_natural_language','Figure 4. zsRE complete-answer development metrics. Values are percentages; no uncertainty intervals are claimed for this single-order screen. CR is the learned-distribution random router (cr_dev_c2_zsre), despite a stale “uniform” label in one prose table. Locality uses the reported development probe set [7].',235)
    p(s,'C2 reaches 99% immediate edit success but retains 30% paraphrase success, compared with 31% for C1, 38% for learned CR and 43% for C0. The corresponding retained exact-edit rates are 94%, 90%, 77% and 99%. Thus the current natural-language screen does not support the central routing advantage. C2 routes about 97% of zsRE deliveries and all CounterFact deliveries to the last bank; the learned CR comparator is deliberately matched to this late-bank preference [7].')
    table(s,['CounterFact development','ES','RET-ES','RET-GS','LS / drift ratio'],[
        ['C0 / C1 / C2 / CR','100%','100%','0%','100% / 1.00'],
        ['B1: LoRA','8%','11%','5.5%','0% / 3.17'],
        ['B3: LoRA + replay','7%','10%','6.5%','0% / 3.94'],
    ],[2.0,.6,.8,.8,1.3])
    p(s,'CounterFact’s calibrated exact-key gate fits original answers but transfers to none of the tested paraphrases. Its zero cap RET-GS is therefore a consequential limitation of this registered retrieval setup. Perfect locality and a drift ratio of 1 on small probes do not establish that the method learns broadly useful corrections. They must be interpreted together with this lack of generalization [7].')
    p(s,'B1 and B3 use rank 8, ten Adam steps and the shared learning rate 1e−4, selected by mean development RET-GS across both datasets. Their weak acquisition and locality restrict the breadth of the baseline comparison. They do not show that cap v0 outperforms all well-tuned editing methods. B4/GRACE would broaden that comparison, but its gate remains failed [2,7,10].','small')

    s=page('6. Mechanistic evidence and interpretation limits')
    p(s,'6. Mechanistic evidence and interpretation limits','h1')
    p(s,'The grammar P4 study asks whether errors associated with different causes occupy different directions in the model’s internal space. It measures the declared eight-step ePC solver on a grammar model trained with backpropagation, not an ePC-trained grammar and not GPT-2 natural-language domains [8].')
    figure(s,'fig05_mechanism','Figure 5. P4 uses 8,192 vectors per cause kind, six block outputs, width 128 and rank-16 bases. A: mean subspace overlap (diagonal is 1 by definition); independent random rank-16 subspaces would have expected overlap 16/128 = 0.125, a reference value rather than a significance test. B: held-out projection capture for matching and nonmatching mechanism changes, averaged over layers [8].',255)
    p(s,'Between-kind overlaps are 0.268–0.351. The bases are stable under resampling (minimum overlap 0.933), and rank 16 captures 98.6% of measured error variance. Held-out private-only and shared-only changes are largely captured by the matching basis (0.963 and 0.994), with lower cross-capture (0.208 and 0.211). This supports a reproducible distinction between these constructed cause kinds [8].')
    p(s,'However, private-versus-private contexts overlap by 0.927. “Private” therefore does not mean a separate orthogonal subspace for each context. Natural-language domain PCA remains unsupported. The appropriate claim is structured grammar error geometry, not a general discovery that unrelated knowledge naturally occupies independent compartments [8].')
    h(s,'Helpful repair is not necessarily the location of the mechanism')
    p(s,'Grammar routing illustrates this distinction: shared-1 deliveries favor bank 1 (89.3%), but shared-2 deliveries reach bank 2 only 2.1%, even though causal tracing identifies bank 2 as its earliest restoring site. A loss-minimizing local write can exploit a downstream shortcut. Router preference, causal tracing, error geometry and retained accuracy are complementary measurements, not interchangeable proof [6,8].')
    p(s,'Production S7 reversals will directly test whether the order of two updates changes retention or damages earlier answers. The repaired harness starts reversals from the same full state, averages damage over every evaluation prefix, preserves original prompt boundaries, and uses disjoint grammar seeds. Its pair inventory is ready; checkpoint outcomes and semantic contradiction review are still due [12].','small')

    s=page('7. GRACE baseline: exclusion and numerical diagnosis')
    p(s,'7. GRACE baseline: exclusion and numerical diagnosis','h1')
    p(s,'GRACE is a retrieved-correction editing baseline being ported to JAX. The port matches all 40 tested greedy-output/NLL comparisons and all keys, radii and labels across 20 isolated and 20 sequential cases. All 40 learned-value comparisons fail, with a maximum absolute gap of 22.439. The conditional registration rule also required a preregistered same-framework sensitivity control to reproduce the divergence class. Its largest reassociation gap was only 0.153, below the fixed 2.244 threshold [9,10].')
    figure(s,'fig06_grace_numerics','Figure 6. Two fixed CPU diagnostic cases. The reference forward graph is unchanged; only the head and loss cotangents are recomputed in float64 during backward replay. The comparison gradient is the unchanged JAX gradient. This experiment localizes a numerical contribution; it is not a repeated optimizer trajectory or a replacement registration control [9].',225)
    p(s,'Round-four diagnostics compare 27 common-input components per case. The initial full-gradient relative gaps are 2.197e−4 and 1.279e−4. Replaying both head and loss reductions in float64 lowers them to 1.438e−5 and 1.001e−5, reductions of about 15.3× and 12.8×. Replacing either reduction alone can worsen the second case because errors partly cancel. A single local discrepancy should not be assigned the whole later value divergence [9].')
    p(s,'The tested JAX reductions are closer to the float64 reference at the localized boundaries. No formula, mask or position-index defect was found in those checks, and no candidate learner repair was justified. The remaining gap is nonzero; the two-case experiment does not explain all 100 optimizer steps or establish that large learned-value differences are harmless [9].')
    callout(s,'Current programme decision','B4 is unavailable in the frozen month programme (DEC-020; updated plan 8). Its 30 comparison jobs are not scheduled. This is a missing baseline, not a failed scientific comparison of C2 against a valid B4. Later inclusion requires a justified gate, a versioned manifest and its own runs [2,10].')
    p(s,'A bounded later study could repeat fixed reduction probes across the already saved parity cases and ask whether early gradient discrepancies predict trajectory differences. It should not search perturbations until a threshold is crossed, relax the current gate after seeing outcomes, or consume the core comparison budget merely to make the port registrable.','small')

    s=page('8. Confirmatory snapshot and a protocol gap')
    p(s,'8. Confirmatory snapshot and a protocol gap','h1')
    p(s,f'At {cutoff.strftime("%H:%M:%S")} EDT, <b>5/210 S4 jobs were complete (2.38%)</b>, with 205 remaining. All five were zsRE/C0, realization 0, orders 0–4, at 300 edits per run. Their saved configuration and metrics agree with the frozen v2 identity, and their before/after base hashes match. There were no v2 failed cells or resource stops in the captured queue. No C2−C1 or C2−CR confirmation is yet available [13].')
    rows=[]
    for r in data['runs']:
        c=r['config'];m=c['metrics']
        rows.append([str(c['perm']),str(c['items_completed']),f"{100*m['es_immediate']['value']:.2f}",f"{100*m['ret_es_end']['value']:.2f}",f"{100*m['ret_gs_end']['value']:.2f}",f"{100*m['ls_complete_answer_end']['value']:.1f}"])
    table(s,['Order','Edits','ES %','RET-ES %','RET-GS %','LS %'],rows,[.6,.6,.8,1,1,.8])
    p(s,'Descriptive C0 results, not a routing comparison. Each row has 300 editing items and 200 locality probes; orders share one realization and can select different 300-item prefixes of its 1,000-item scope. C0’s 300-edit endpoint cannot be compared directly with another arm’s 1,000-edit endpoint. Do not pool the rows as five independent samples [2,13].','caption')
    h(s,'Failure encountered and repaired before v2')
    p(s,'The original v1 freeze produced 50 no-item failures: a loader incorrectly applied a realization-filename rule to the grammar’s .npz resource binding. No edited-item results were produced. The attempts were archived, the loader received a regression, and the queue now stops after three consecutive no-item failures. A newly frozen v2 binds the repaired source. The incident shows why passing component controls did not guarantee a usable end-to-end queue [2].')
    callout(s,'New finding: LM-drift coverage does not meet the plan','The PDF requests one million WikiText-103 validation tokens. SD-3 explicitly substitutes the whole available split: 247,289 unique tokens (DATA-04). S4 instead requests 4,096; its evaluator scores 32 windows × 127 next-token positions = 4,064 positions. Every row above reports that count, and S5 also selects 4,096. This is about 1.64% of the approved split’s token count; window boundaries also affect the exact scored-position denominator [1,2,13,15,17].')
    p(s,'All five rows report drift ratio 1.00 on that small sample. The result may be correct for those positions, but it does not complete the whole-split assay authorized by SD-3. This review found no authorization for that further reduction. The lead should assess a versioned repair or an explicitly approved, checkpoint-based completion of the missing evaluation, with all cost charged. Changing the frozen source silently is not an acceptable remedy. The review itself has not altered or stopped the active queue.')
    p(s,'Locality here is also the 200-prompt development unrelated pool, not evidence of complete near-neighbour challenge coverage. The registered challenge sets and their separate reporting remain necessary. The drift discrepancy does not by itself prove ES or RET-GS wrong; it limits protocol completion and the scope of collateral-damage claims.','small')

    s=page('9. Verification, reproducibility and evidence quality')
    p(s,'9. Verification, reproducibility and evidence quality','h1')
    p(s,'The project has substantial correctness evidence, including independent review and repaired counterexamples. Such controls verify specified behavior on their inputs; they do not establish statistical superiority or guarantee that every reporting contract has been implemented. The newly found drift gap illustrates the remaining distinction [11,12,14,15].')
    table(s,['Evidence group','What is established','Boundary'],[
        ['Core controls PC-1…PC-9','Acquisition fixtures, exact cap-off identity, idempotence, rollback, signed probes, budgets, complete-answer scoring, read-only evaluation and cloning.','The table in docs/controls.md distinguishes CPU and GPU evidence and implemented variants.'],
        ['Round-four CPU audit','63 controls/known-answer tests, including the full PC-1 fixture; eight snapshot/resource/collector tests; nine S7 regressions.','PC-10 is explicitly excluded as a known failure; counts are not line coverage.'],
        ['GPU window 2','46 GPU tests, including real-artifact identity checks and negative refusals.','Previously recorded evidence reviewed here; no GPU rerun for this paper.'],
        ['Environment recreation','ENV-05 recreated the scratch environment with 150/150 pinned packages.','An install audit is distinct from full research-result reproduction.'],
        ['Reproduction pre-audit','27 CPU command invocations; 24 initially returned zero; three issues were examined in isolated follow-ups.','A sibling path, an assets-relative data path and completed-output rerun semantics required clarification.'],
    ],[1.2,2.7,2.5])
    h(s,'What the two agents have contributed')
    p(s,'The execution agent has built the apparatus, regenerated and characterized the substrate, calibrated the cap and baselines, repaired reviewed defects, prepared the frozen schedule and started confirmation. Codex’s concurrent work has supplied baseline-parity diagnostics, independent harness and S7 reviews, control coverage, resource/collector checks and reproduction pre-audits. Implementation and independent review have strengthened the apparatus; control pass counts remain distinct from efficacy [2,9,11,12,14].')
    h(s,'A version-aware evidence trail is essential')
    p(s,'Several narrative summaries lag behind the machine artifacts: ongoing notes still contain an old “GPU idle” statement; the queue summary describes a bounded earlier session; a CR row is mislabeled uniform; P6 retains a stale BP-wrapper description despite its actual ePC checkpoint path; and the full P1 file was later replaced by a smaller follow-up. This paper resolves those cases using frozen identity, saved values and Git history, and captures the actual source bytes in its evidence bundle [2,4,7,13].')
    p(s,'The reproducibility follow-up reports 356 passed, five skipped and 52 deselected CPU tests with the sibling resource path explicit. This is a scoped command result, not “all tests pass.” Before final delivery, the owner should rerun the documented commands against the final artifact set and retain both failed attempts and their resolved successors [14].','small')

    s=page('10. Resource outlook: accounting before confidence')
    p(s,'10. Resource outlook: accounting before confidence','h1')
    p(s,'The original plan assigns 154 A100-equivalent hours across S0–S8. Actual work runs on a local RTX 5070 with 12 GiB memory. The conversion κ = 1 local hour per A100-equivalent hour is provisional, with a declared 0.5–2 sensitivity band and no measured A100 reference. Local measurements should therefore be reported directly alongside the provisional normalization [1,16].')
    figure(s,'fig07_resources','Figure 7. Recorded local accelerator cost versus projections. Dashed markers show frozen allowances after 25% headroom: S4 27 h and S5 18 h. *The second row only subtracts the excluded B4 components (5.47 h) from the selected S4 arithmetic; it is not a refreshed queue or evaluation-cost model. REG-02 is observed consumption and is charged to S6, not added to S4 [2,3,16].',220)
    p(s,f'The selected S4 projection is {s4h:.2f} h, but still contains {b4h:.2f} h of assumed B4 work even though B4 is unavailable. Removing those terms gives {s4h-b4h:.2f} h arithmetically. Grammar costs are now measured despite a stale “unpriced” status string. Neither calculation incorporates a whole-validation drift assay under SD-3. The practical next step is an accounting reconciliation against the frozen scheduled jobs and actual evaluation requirements, without retuning the scope from outcomes [16].')
    p(s,f'S5 is projected at {s5h:.2f} h against an 18 h allowance. It uses SE-A/SB and SE-E/SB factors of 0.991 and 1.357 from a 20-item zsRE smoke test, extrapolated to CounterFact. SB reuses S4 C1 runs and is charged once. These are useful planning estimates, but setup, rescoring, sequence lengths, stream growth and dataset differences can change the ratios [16].')
    h(s,'Why accelerator hours are not an elapsed-time promise')
    p(s,f'The captured progress tool estimates {progress["eta_hours_remaining"]:.1f} wall-hours remaining for S4. Only {progress["eta_basis"]["observed"]} remaining jobs use observed same-arm timing; {progress["eta_basis"]["projected"]} rely on projection, including a fixed 2.5 wall/accelerator multiplier. The median observed C0 queue time is {progress["per_arm"]["zsre/C0"]["wall"]:.1f} seconds. This is a heuristic ETA, not a confidence interval or a measured rate for C1, C2, CR, B3 and grammar [13].')
    p(s,'Per-run allowances are 2,400 accelerator seconds; stage allowances are 97,200 for S4 and 64,800 for S5. Resource stops preserve the completed prefix and charge failed work. Checks at item boundaries can overshoot by in-flight work. Final evaluation and all archived attempts must remain in the audit. At κ = 2, the existing scope table has no affordable selection; normalization uncertainty is a material budget issue, not a reason to silently increase the budget [2,16].','small')

    s=page('11. Timeline assessment and the critical path')
    p(s,'11. Timeline assessment and the critical path','h1')
    p(s,'D0 is 9 September 2026 (DEC-000); this snapshot is day 3 of the month programme. The plan was revised on 7 September and the repository began earlier than D0, so neither date should be mistaken for the execution clock. The original schedule placed foundation work in week 1, mechanism screening and freeze in week 2, confirmation in week 3, and final synthesis in week 4 [1,2].')
    figure(s,'fig08_timeline','Figure 8. Approximate windows from the original month plan, alongside the day-3 evidence state. The early start of S4 is real implementation progress. Bar lengths are planned calendar windows, not measured completion or promises about remaining work [1,2,13].',220)
    callout(s,'Schedule judgment','Implementation and freeze milestones have arrived earlier than their original windows. Overall completion cannot yet be called secure: only 2.38% of S4 jobs are finished, the required contrasts are absent, S5 and S7 outcomes remain, and the unresolved drift-evaluation gap can change the critical path. A task-board completion count is not a measure of completed scientific evidence.')
    p(s,'Updated plan 8 estimates about 60–80 wall-hours for S4 and 30–40 for S5 when serialized on the GPU lease. Together those planning ranges imply roughly 3.75–5 days of uninterrupted device availability before subsequent work, excluding any evaluation repair. The later live S4 heuristic is shorter, but mostly extrapolated. These estimates are compatible with the original month window under favorable operation; they do not establish that the project is ahead by a specific number of days [2,13].')
    p(s,'The next bottleneck is accepted, complete paired evidence. S4 must yield matched required-arm coverage; S5 can follow or interleave by realization once reusable C1 runs exist. S7 depends on committed 300-edit or grammar task-4/8 checkpoints, fixed pairs and semantic review. Final S8 audit and reporting depend on those outputs, the cost ledger and resolution of reporting gaps [2].')
    p(s,'S6 conditional re-distillation is closed for this month (DEC-022), because regeneration used much of that allocation and a matched continuation pair does not fit. A future proposal may be written from S5 evidence, but S6-02…05 are not scheduled. This is an explicit scope decision, not a task that should silently return to the GPU queue.','small')

    s=page('12. Risks, decisions and available parallel work')
    p(s,'12. Risks, decisions and available parallel work','h1')
    table(s,['Issue / priority','Consequence','Next action and boundary'],[
        ['Drift sample mismatch — immediate','The 4,064-position results do not cover the approved validation split; a correction may materially alter cost and schedule.','Lead: decide a documented, versioned remedy. CPU reviewer: specify expected coverage and checkpoint evidence. Any GPU rescore uses the lease.'],
        ['Missing comparative evidence — high','Five C0 orders cannot establish C2 superiority or ePC benefit.','Run owner: finish frozen pairs before optional experiments; analysis owner: reject missing cells, mismatched scopes and mixed identities.'],
        ['Only three independent realizations — high','Intervals have limited resolution and may underrepresent broader uncertainty.','Retain all orders and show realization-level effects. Report qualified/inconclusive outcomes honestly; expand replication only in a later protocol.'],
        ['Exact-key generalization limit — high','CounterFact cap RET-GS is zero in development; grammar paraphrases remain at the base floor.','Keep RET-GS primary. Diagnose retrieval and feature invariance separately; preregister future retrieval changes rather than switching the endpoint.'],
        ['GPU / budget forecast — high','One device, extrapolated costs, provisional κ and a larger drift assay could exhaust headroom.','CPU: reconcile ledgers and excluded B4 pricing. GPU owner: preserve complete pairs, monitor resource stops and serialize expensive jobs.'],
        ['Baseline breadth — moderate','B4 is unavailable; B1/B3 development acquisition is weak.','Disclose the missing contrast and tuning rule. Continue B4 numerics only as bounded, separate diagnostics.'],
        ['S7 pair semantics — moderate','CounterFact shared pairs number 9 instead of the target 34; structural strata are only proxies.','CPU: semantic contradiction review before outcomes. Retain stratum counts and qualification; production reversals await checkpoints.'],
        ['Provenance drift — moderate','Overwritten summaries and stale labels can lead to unsupported claims.','CPU: preserve immutable evidence copies, full P1 history, source hashes and per-claim denominators; final reproduction checks the release bundle.'],
    ],[1.4,2.1,2.8])
    p(s,'Concurrency does not require shared-source edits. Independent CPU lanes can prepare coverage validators, review the pair inventory, audit resource arithmetic, write evidence tables and reproduce reporting commands in new output locations. Claude retains the active run queue and GPU lease. No agent should change the frozen src/pccap tree without the versioned approval process [2,11–16].','small')

    s=page('13. Remaining checkpoints and scientific direction')
    p(s,'13. Remaining checkpoints and scientific direction','h1')
    table(s,['Checkpoint','Concrete completion evidence'],[
        ['Resolve evaluation contract','A lead decision on the drift mismatch; a named sample, recorded evaluated-position count, matching checkpoints, proper cost treatment and a plan-conformant report or explicit disclosed limitation.'],
        ['S4: finish and audit','Complete required C1/C2/CR matrices for each dataset and frozen scope; paired 97.5% intervals, ES/LS constraints, cost views and resource-stop accounting. Keep C0 and B3 comparisons scope-aware.'],
        ['S5: isolate substrate from credit','SB = BP + C1 + adjoint (reused); SE-A = ePC + C1 + adjoint; SE-E = the same ePC + C1 + eight-step error credit. Report SE-A−SB separately from SE-E−SE-A.'],
        ['S7: direct interference','Semantically reviewed fixed pairs, correct selection hash, identical reversal starts and complete-prefix damage; report both orders and all strata, including the nine-pair CounterFact shared stratum.'],
        ['S8: final deliverable','Reproduce the final artifact set, reconcile all costs and deviations, issue positive/qualified/inconclusive/negative classifications, and complete licensing/publication review (T4).'],
    ],[1.4,4.6])
    h(s,'Where the evidence suggests focusing next')
    p(s,'First, complete the registered comparison and resolve evaluation coverage. The natural-language development signal is not a reason to abandon a controlled negative result: it may show that this measured router spends extra probing effort while behaving mostly like a late-bank editor. Compare C2 with learned CR at measured cost, and examine acquisition, forgetting and retrieval failures separately.')
    p(s,'Second, keep exact recall and generalization distinct. If exact-key retrieval remains the dominant bottleneck, a future study could test more paraphrase-stable keys or a different retrieval rule under the same locality and memory constraints. Those changes need a new development phase and frozen experiment; current RET-GS must not be replaced after results become visible.')
    p(s,'Third, retain the substrate/credit separation. The regenerated model is highly faithful but only slightly different from BP, and its errors are not settled at the chosen iteration count. An absent SE-A gain would limit claims about this conversion, while an SE-E difference would concern finite-iteration credit. Neither result alone settles the general value of predictive coding.')
    p(s,'The frozen exploratory list includes cap-disabled keys versus ordinary residual keys, half/double memory, difficulty weighting, and optional error/gradient keys only if their implementation and isolation controls exist. These are three-realization, two-order exploratory studies, dropped before any core pair. Optional Hessian diagnostics and additional re-distillation should not displace direct order-effect tests or the main evidence [1,2,11].')
    h(s,'Conclusion')
    p(s,'The working apparatus demonstrates controlled acquisition, substrate fidelity and reproducible synthetic error structure. The main continual-learning advantage remains unproven. A rigorous finish requires complete paired outcomes, resolution of drift-evaluation coverage and transparent costs. A well-supported negative result would also be a useful outcome.')

    s=page('Supplementary property scorecard: P2, P3 and P5')
    p(s,'Supplementary property scorecard: P2, P3 and P5','h1')
    p(s,'The substrate programme includes three further diagnostics that help explain what the base makes available to a cap. They describe feature diversity, gradient concentration and the reach of writes. They do not replace retained-answer comparisons, and geometric quantities depend on the chosen coordinates [1,18].')
    figure(s,'fig09_feature_rank','Figure 9. Effective rank summarizes how many directions carry substantial feature variation; it is not an accuracy score or a count of stored facts. Values use 4,096 sampled positions on the regenerated ePC base. Site labels follow the recorded P2 convention, including the pre-final-normalization site at block 12. No uncertainty interval is inferred [18].',195)
    table(s,['Diagnostic','Observed result','Interpretation'],[
        ['P2: representation structure','Effective rank 103.3 at the embedding, peak 349.4 at site 9, and 104.4 at site 12. Best part-of-speech probe accuracy 91.81% on 5,040 held-out labels.','Features carry recoverable linguistic information; neither rank nor a probe establishes better continual learning.'],
        ['P3: adjoint localization','1,000 sequences; raw normalized participation ratio 0.1745; final-block share 0.01098. Layer-normalized participation ratio 0.1158.','The diagnostic uses the BP adjoint on the ePC base. Gradient mass is not all at the last block; coordinates and layer normalization change the statistic.'],
        ['P5: write locality','200 edit prompts and 200 unrelated probes. Banks 1/2/3 achieve a 50% current-token loss reduction on 94.5% / 100% / 100% of edit prompts.','Median normalized write norms at the target are 0.80 / 0.20 / 0.05. Ease of correcting one token is distinct from retained complete-answer success.'],
    ],[1.2,2.7,2.5])
    p(s,'P5’s mean unconditional collateral KL is 1.086, 0.137 and 0.202 nats for banks 1–3, respectively. This deliberately applied-write assay is different from deployed retrieval gating. A separate A = 0.3 development gate screen records zero firings on 1,000 unrelated probes per dataset; that is finite probe evidence, not a universal locality guarantee [18].')
    p(s,'These diagnostics help explain why useful routes and anatomical mechanisms need not coincide: late writes can reduce immediate loss with smaller normalized increments, although most raw gradient mass lies elsewhere. Retrieval-key drift still requires saved-learner checkpoint analysis. The stronger question—whether such local advantages improve acquisition, retention and sharing at matched cost—remains with S4, S5 and S7.','small')

    s=page('References, data availability and provenance')
    p(s,'References and data availability','h1')
    p(s,'References below identify local primary evidence, relative to the pc_cap repository. The accompanying evidence_final.json captures source contents and SHA-256 hashes at the stated cutoff; it includes aggregate completed-run records but no sealed item manifests. Figures are generated from that snapshot, not from hand-entered visual estimates. The original plan PDF is the scientific authority; decisions document subsequent operational resolutions.','small')
    refs=[
        ('1','Goertzel, B., & Fable, C. (2026). A One-Month Programme for Continual-Learning Predictive-Coding Caps on GPT-2-Scale Transformers. Readable edition, revised 7 September.','docs/pc_cap_month_plan_readable.pdf; extracted text: docs/pdf_text/plan.txt'),
        ('2','Frozen protocol, decisions and current plan delta. DEC-000, 020, 022, 025–027; freeze timestamp is read from the manifest.','manifests/frozen.json; docs/decisions.md; docs/updated_plan8.md; docs/ongoing.md'),
        ('3','REG-02 regeneration and preflight.','results/REG/epc-50m/summary.json; results/REG/preflight.json'),
        ('4','Substrate fidelity and finite-iteration credit diagnostics. Full P1 is the historical blob at commit 25c988b; the current P1 is a smaller follow-up.','git show 25c988b:results/S1/P1_epc.json; results/S1/P1_epc.json; results/S1/P6_epc.json'),
        ('5','Constructed fixture study.','results/S3/fixture/summary.json'),
        ('6','Replacement grammar development and routing versus tracing.','results/S3/grammar_dev_matrix.json'),
        ('7','Revised natural-language development and random-router policy.','results/S2/throughput_v2.json; results/S2/throughput_v2_baselines.json; manifests/cr_distribution.json'),
        ('8','Grammar error geometry, P4.','results/S1/P4_gram.json'),
        ('9','GRACE round-four localization and backward replay.','results/S2/grace_jax/gradient_localization/{candidate,head_loss_probes,reduction_replay_candidate}.json; logs/grace_gradient_localization.md'),
        ('10','GRACE registration gate and preregistered sensitivity.','results/S2/grace_jax/pc10.json; results/S2/grace_jax/sensitivity.json; docs/updated_plan8.md'),
        ('11','Control coverage and round-four CPU audit.','docs/controls.md; results/S3/control_audit_round4/run.json'),
        ('12','Independent S7 repair and pair-inventory review.','logs/review_p4_s7_r2.md'),
        ('13','Completed v2 run records and queue snapshot (12:39:45 EDT).','results/S4/frozen-confirmatory-v2-84126123/zsre/C0/BP/h/0/{0,1,2,3,4}/{config,metrics}.json; results/S4/queue.jsonl; results/S4/jobs.json; scripts/s4_progress.py'),
        ('14','Environment and reproduction evidence.','docs/environment.md; docs/REPRODUCE.md; logs/reproduce_preaudit.md; logs/reproduce_round4/{summary,followup}.json'),
        ('15','Analysis implementation and evaluation coverage.','src/pccap/analysis/{bootstrap,paired}.py; src/pccap/harness/{stage_s4,stage_s5,stage_s3,runs}.py'),
        ('16','Projection and provisional hardware conversion.','results/S2/projection.json; results/S5/projection.json; results/ENV/kappa.json'),
        ('17','Approved whole-validation drift corpus (SD-3 / PA-5); 247,289 unique tokens.','docs/spec_defects.md; docs/tasks/DATA-04.md; manifests/dev/lm_sets.json'),
        ('18','Additional regenerated-substrate property diagnostics.','results/S1/P2_epc.json; results/S1/P3_epc.json; results/S1/P5_epc.json'),
    ]
    for n,title,path in refs:
        p(s,f'<b>[{n}]</b> '+escape(title),'small');p(s,escape(path),'mono')

    s=page('Technical appendix: identity and reading guide')
    p(s,'Technical appendix: identity and reading guide','h1')
    h(s,'Bound identities at the evidence cutoff')
    for label,value in [
        ('Experiment',data['experiment_id']),('Evidence cutoff (UTC)',data['capture_finished_utc']),
        ('Repository HEAD at capture',data['git_head']),('Frozen manifest SHA-256',data['frozen_sha256']),
        ('Frozen src/pccap tree SHA-256',frozen['code_commit']['src_tree_sha256']),
        ('Plan PDF SHA-256',data['plan_pdf_sha256']),('Frozen environment lock SHA-256',frozen['env_lock_sha']),
        ('Regenerated checkpoint SHA-256',source('results/REG/preflight.json')['params_sha256']),
    ]:
        p(s,'<b>'+label+'</b>','small');p(s,escape(str(value)),'mono')
    p(s,'The freeze records a dirty working tree and an earlier Git HEAD because the lead commits separately. The frozen source-tree hash is therefore the operative code identity; a later repository commit alone does not imply different scientific code. The active queue continued after this report’s cutoff. None of its later results are silently included [2,13].','small')
    h(s,'Compact glossary')
    table(s,['Term','Reading guide'],[
        ['Predictive coding / ePC','A model formulation with explicit errors and iterative inference; here, error-optimizing predictive coding. This month also studies a simpler correction memory motivated by that idea.'],
        ['Adjoint / credit','The gradient of loss with respect to an internal vector / the signal used to choose a correction direction.'],
        ['KL / NLL / nats','Distribution discrepancy / negative log-likelihood / natural-log units. Lower usually indicates closer distributions or less prediction loss.'],
        ['Realization / order','A sampled set of learning items / a permutation of that set. Orders share a realization and are statistically dependent.'],
        ['Frozen protocol / checkpoint','A bound experimental specification / a saved learner state. Freezing a protocol does not mean every part of the implementation is already proven correct.'],
    ],[1.25,4.5])
    p(s,'Reproduction: use capture_status_evidence_v2.py only for a new dated snapshot. Build this exact paper from the saved evidence_final.json using build_status_paper_v4.py and a new output directory. The renderer records layout checks and exports all nine figures as PNG and vector PDF. Findings are limited to GPT-2-scale editing and synthetic tasks; broader domain adaptation is deferred. The paper contains no new GPU experiment and does not change production code, thresholds, task boards or prior evidence.','small')

    # Validate every explicit page before publishing any PDF bytes.
    buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=A4,pageCompression=1)
    c.setTitle('pc_cap — Current research status — 11 September 2026')
    c.setAuthor('pc_cap project; evidence synthesis prepared by Codex')
    c.setCreator('pc_cap status-paper renderer; ReportLab and Matplotlib')
    c.setSubject('Interim scientific report: evidence, confirmation, timeline, risks and remaining work')
    c.setKeywords('predictive coding, continual learning, GPT-2, cap, JAX, interim research')
    layout=[]
    for i,(title,story) in enumerate(pages,1):
        c.bookmarkPage(f'page-{i}');c.addOutlineEntry(title,f'page-{i}',level=0)
        c.setStrokeColor(colors.HexColor('#B7CCD5'));c.setLineWidth(.5)
        c.line(44,height-40,width-44,height-40)
        c.setFont('Sans',7.3);c.setFillColor(colors.HexColor(GRAY))
        c.drawString(44,height-30,'PC_CAP  |  CURRENT RESEARCH STATUS')
        c.drawRightString(width-44,height-30,'Evidence: 11 Sep 2026, 12:39:45 EDT')
        c.line(44,40,width-44,40)
        c.drawString(44,27,'Interim evidence synthesis • development ≠ confirmation')
        c.drawRightString(width-44,27,f'{i} / {len(pages)}')
        frame=Frame(44,52,usable,height-105,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        remaining=list(story)
        frame.addFromList(remaining,c)
        layout.append({'page':i,'title':title,'remaining_flowables':len(remaining),'unused_height_points':round(frame._y-frame._y1p,2)})
        if remaining:
            raise RuntimeError(f'Page {i} overflows by {len(remaining)} flowables: {title}')
        c.showPage()
    c.save()
    pdf_bytes=buf.getvalue()
    with (out/'paper.pdf').open('xb') as f:f.write(pdf_bytes)
    with (out/'manuscript.md').open('x') as f:f.write(''.join(manuscript))
    verification={'pages':len(pages),'figures':len(figures),'layout':layout,
        'pdf_sha256':hashlib.sha256(pdf_bytes).hexdigest(),
        'evidence_sha256':hashlib.sha256(args.evidence.read_bytes()).hexdigest(),
        'renderer_versions':{'matplotlib':matplotlib.__version__},
        'graph_values':{'s4_projected_hours':s4h,'excluded_b4_hours':b4h,'s4_subtraction_only_hours':s4h-b4h,'s5_projected_hours':s5h},
        'scientific_experiments_run':0,'gpu_seconds':0,
    }
    with (out/'build_checks.json').open('x') as f:json.dump(verification,f,indent=2)
    print(json.dumps(verification,indent=2))


if __name__=='__main__':
    main()
