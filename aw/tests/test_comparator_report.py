"""Actual 225-cell snapshot checks; no experiment or re-scoring."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from aw.comparator_report import groups, unavailable_reason
from aw.pc_historical import Sources
from aw.pc_v0_report import sha

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'logs/R1/reports/comparators-225'


@pytest.fixture(scope='module')
def analysis():
    return json.loads((OUT/'analysis.json').read_bytes())


def test_boundary_and_all_comparator_slots(analysis):
    assert len(analysis['cells'])==330
    assert analysis['complete_blocks']==[1,2,3,4]
    assert sum(c['artifact_complete'] for c in analysis['cells'])==225
    assert all(not c['checkpoints'] for c in analysis['cells'] if c['block_number']>4)
    assert sum(len(c['metrics']) for c in analysis['contrasts'])==63
    for source,expected in analysis['analysis_source_sha256'].items():
        assert sha(Sources().resolve(ROOT/source,expected))==expected


def test_registered_inference_and_unchanged_triplet(analysis):
    available=[c for c in analysis['contrasts'] if c['classification']!='unavailable']
    assert len(available)==10
    assert sum(c['classification']=='positive' for c in available)==6
    assert sum(c['classification']=='inconclusive' for c in available)==4
    for c in available:
        for v in c['metrics'].values():
            means=np.asarray(v['realization_estimates'])
            assert len(means)==3
            assert v['estimate']==pytest.approx(means.mean())
            assert v['adjusted_interval']['lower']==pytest.approx(means.min())
            assert v['adjusted_interval']['upper']==pytest.approx(means.max())
            assert len(v['preliminary']['order_dispersion'])==3
            assert all(len(x['order_values'])==5 for x in v['preliminary']['order_dispersion'])
            delta=4.302652729696142*np.std(means,ddof=1)/math.sqrt(3)
            assert v['preliminary']['t_sensitivity']['lower']==pytest.approx(means.mean()-delta)
            assert v['preliminary']['t_sensitivity']['upper']==pytest.approx(means.mean()+delta)
    old=json.loads((ROOT/'logs/R1/reports/triplet/analysis.json').read_bytes())
    for contrast in old['contrasts']:
        if contrast['classification']!='unavailable':
            assert contrast==next(c for c in analysis['contrasts'] if c['dataset']==contrast['dataset'] and c['contrast']==contrast['contrast'])


def test_realizations_and_missing_reasons(analysis):
    result=groups(analysis)
    assert len(result)==45 and all(r['full_order_grid'] for r in result)
    assert all(r['checkpoint']==300 for r in result if r['dataset']=='mquake')
    assert 'DEC-074b' in unavailable_reason('counterfact','S1_literal',225)
    assert 'DEC-066' in unavailable_reason('mquake','matched_update',270)
    assert '300' in unavailable_reason('mquake','v0_stable',225)
    report=json.loads((OUT/'report.json').read_bytes())
    assert len(report['unavailable'])==14
    partial=dict(analysis,cells=analysis['cells'][1:])
    r=next(g for g in groups(partial) if (g['dataset'],g['condition'],g['realization'])==('zsre','R1_learned_ff',0))
    assert r['complete_orders']==4 and not r['full_order_grid']


def test_cost_inventory_watch_and_no_unknowns():
    cost=json.loads((OUT/'accounting.json').read_bytes())
    assert len(cost['rows'])==225
    assert cost['charged_hours']==pytest.approx(sum(r['charged_seconds'] for r in cost['rows'])/3600)
    assert cost['failures']==cost['retries']==cost['unknown_attempts']==0
    assert cost['missing_parent_decisions']==2
    assert all(r['process_attempts']==1 and r['uncovered_driver_seconds']==0 for r in cost['rows'])
    appendix=json.loads((OUT/'appendix/report-data.json').read_bytes())
    assert appendix['watch']['queue_observations']==225
