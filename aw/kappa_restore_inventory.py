"""KP-1: deserialize pilot stream checkpoints on CPU, without a base or model call."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

import numpy as np

import pccap  # noqa: F401 -- initialize before JAX imports in reader
from pccap.harness.snapshot import restore
from pccap.revision_v1.reader import params_hash

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def run(output):
    rows, sources = [], {}
    def read(p):
        sources[str(p.resolve())] = sha(p)
        return json.loads(p.read_bytes())
    for arm in ('ordinary', 'kappa02', 'kappa05'):
        for seed in range(3):
            name = f'r1_50_stream_sel6_text_s{seed}' if arm == 'ordinary' else f'ht3_{arm}_s{seed}'
            for ds in ('zsre', 'counterfact', 'mquake'):
                drift = read(ROOT / f'results/R1/drift_assay_ht3_{name}_{ds}.json')
                theta = Path(drift['theta'])
                sources[str(theta)] = sha(theta)
                params = {}
                with np.load(theta, allow_pickle=False) as data:
                    for key in data.files:
                        keys = [ast.literal_eval(v) for v in re.findall(r"\[([^]]+)\]", key)]
                        if not keys:
                            raise ValueError('unrecognized parameter archive key')
                        current = params
                        for part in keys[:-1]:
                            current = current.setdefault(part, {})
                        current[keys[-1]] = data[key]
                def sequences(node):
                    if not isinstance(node, dict):
                        return node
                    if all(isinstance(k, int) for k in node):
                        assert sorted(node) == list(range(len(node)))
                        return [sequences(node[k]) for k in range(len(node))]
                    return {k: sequences(v) for k, v in node.items()}
                params = sequences(params)
                tag = name + '_stepavg_rare1_null0.5' + ('' if ds == 'zsre' else '@' + ds)
                stream = read(ROOT / f'results/R1/stream_eval_{tag}.json')
                cp = read(ROOT / f'results/R1/streams_revision/{tag}/checkpoints.json')[-1]
                snapshot = ROOT.parent / f'assets/runs/R1/streams_revision/{tag}/learner_end.ckpt'
                actual = sha(snapshot)
                assert actual == cp['checkpoint_sha256']
                sources[str(snapshot)] = actual
                state = restore(snapshot.read_bytes(), expected_hash=cp['state_hash'])
                assert params_hash(params) == stream['theta_hash'] == state.scalars['params_hash']
                config = json.loads(state.scalars['config'])
                rows.append(dict(arm=arm, seed=seed, dataset=ds, reader=str(theta), reader_file_sha256=sha(theta),
                                 reader_params_sha256=stream['theta_hash'], snapshot=str(snapshot), snapshot_sha256=actual,
                                 stream_state_sha256=cp['state_hash'], stream_snapshot_verified=True,
                                 edits=cp['items'], ordered_ids=[r['item_id'] for r in cp['rows']],
                                 stream_args=stream['args'], config=config, drift_summary=drift,
                                 drift_memory_snapshot=None, drift_memory_state_hash=None,
                                 original_drift_memory_equality='unproven: assay saved neither state nor state identity'))
    for name in ('scripts/r1_54_drift_assay.py', 'scripts/r1_13_stream_eval.py',
                 'src/pccap/harness/stage_s2.py', 'manifests/revision_v1/kappa_pilot_v3.json',
                 'manifests/revision_v1/stop_tokens_v1.json',
                 'manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json'):
        sources[str(ROOT / name)] = sha(ROOT / name)
    for path in (Path(__file__).resolve(), ROOT / 'src/pccap/harness/snapshot.py', ROOT / 'src/pccap/revision_v1/reader.py'):
        sources[str(path)] = sha(path)
    output.mkdir(parents=True, exist_ok=False)
    value=dict(task='KP-1', decision='NO-GO for an exact continuation of the original drift memories',
               reason='Stream snapshots restore exactly, but the separately built drift memories have no saved identity to compare. No reacquisition or model execution is authorized by this inventory.',
               rows=rows, verified_stream_snapshots=len(rows), unique_readers=9,
               sources_sha256=sources, model_calls=0, gpu_seconds=0,
               owner_execution_command=None,
               hypothetical_readout_hours={'one_dataset_nine_cells':3.75,'two_datasets_18_cells':7.5,'three_datasets_27_cells':11.25})
    (output / 'inventory.json').write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:value[k] for k in ('decision','verified_stream_snapshots','unique_readers')}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
