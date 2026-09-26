"""Report integrity and incomplete-pair behavior, plus the real CPU runner smoke."""
import copy
import json

import pytest

from aw.pc_v0_report import ROOT, build, compare, expected_cells, load_group

SMOKE = ROOT/'results/additional_work/PC-v0/cpu-smoke-round45'


def test_empty_plan_retains_every_slot(tmp_path):
    result = build([], tmp_path/'out', tmp_path/'report.md')
    assert len(result['cells'])==12 and len(result['pairs'])==6
    assert all(a['mean'] is None for a in result['aggregates'])
    assert '0/12' in (tmp_path/'report.md').read_text()


def test_partial_pair_never_enters_mean():
    cells = expected_cells(1)
    rows=[]
    for c in cells:
        rows.append(dict(c,status='complete', metrics={k: .2 if c['arm']=='SE-A' else .5 for k in ('ES','RET-ES','RET-GS','LS')},
                         secondary={k:0. for k in ('bounded_es_immediate','bounded_ret_es_end','bounded_ret_gs_end','bounded_ls_end')}))
    _,_,a=compare(rows,cells)
    assert a[0]['mean']==pytest.approx(.3)
    rows[0]['status']='wall_stop'
    _,pairs,a=compare(rows,cells)
    assert pairs[0]['difference']['ES'] is None and a[0]['mean'] is None
    assert a[0]['realizations'][1:]==pytest.approx([.3,.3])
    with pytest.raises(ValueError,match='duplicate'):
        compare(rows+rows[:1],cells)


def test_actual_runner_smoke_output_and_hash_checks(tmp_path):
    assert SMOKE.exists(), 'Generate the CPU runner smoke first (documented PC-3 command)'
    rows = load_group(SMOKE,{},smoke=True)
    assert len(rows)==2 and all(r['status']=='complete' for r in rows)
    result=build([SMOKE],tmp_path/'report',tmp_path/'report.md',smoke=True)
    assert result['pairs'][0]['status']=='complete'
    assert 'CPU SMOKE ONLY' in (tmp_path/'report.md').read_text()
    with pytest.raises(ValueError,match='populations'):
        load_group(SMOKE,{})
    copied=tmp_path/'altered'
    import shutil
    shutil.copytree(SMOKE,copied)
    config=copied/'zsre-r0-o100-SE-E/config.json'
    value=json.loads(config.read_text())
    value['item_ids']=['different-item']
    config.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='paired arms differ'):
        build([copied],tmp_path/'bad',tmp_path/'bad.md',smoke=True)
    value['sources']=copy.deepcopy(value['sources'])
    value['sources']['aw/pc_v0.py']='0'*64
    config.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='sources differ'):
        load_group(copied,{},smoke=True)


def test_missing_finish_and_corrupt_completion(tmp_path):
    import shutil
    copied=tmp_path/'incomplete'
    shutil.copytree(SMOKE,copied)
    finish=copied/'zsre-r0-o100-SE-E/finish.json'
    value=json.loads(finish.read_text())
    finish.unlink()
    rows=load_group(copied,{},smoke=True)
    assert rows[1]['status']=='unfinished'
    value['items_completed']=0
    finish.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='disposition'):
        load_group(copied,{},smoke=True)


def test_real_solver_diagnostics_render_and_reject_missing_horizon(tmp_path):
    import shutil
    copied=tmp_path/'diagnostic'
    shutil.copytree(SMOKE,copied)
    plan=json.loads((copied/'plan.json').read_bytes())
    plan['cells']=plan['cells'][:1]
    (copied/'plan.json').write_text(json.dumps(plan))
    dest=copied/'zsre-r0-o100-SE-A'
    rows=json.loads((copied/'tiny-diagnostic.json').read_bytes())
    value={'rows':[{'item_id':'synthetic-0','prefix_ids':[4,11],'target':17,'writes':'zero','diagnostics':rows}]}
    (dest/'diagnostics.json').write_text(json.dumps(value))
    result=build([SMOKE],tmp_path/'out',tmp_path/'report.md',smoke=True,diagnostics=[copied])
    assert len(result['diagnostics'])==1
    assert '| zsre | synthetic-0 | 2 | zero | 32 |' in (tmp_path/'report.md').read_text()
    value['rows'][0]['diagnostics']=rows[:2]
    (dest/'diagnostics.json').write_text(json.dumps(value))
    with pytest.raises(ValueError,match='horizon inventory'):
        load_group(copied,{},smoke=True,diagnostic=True)
