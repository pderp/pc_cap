"""Tiny CPU execution of the same stream/evaluator used by PC-v0; no research data."""
import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import time
from pathlib import Path

import numpy as np

from aw.pc_v0 import SupplementalEvaluator, credit_diagnostics
from aw.pc_v0_report import ROOT, sha
from aw.tests.test_pc_v0 import TinyEPC
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget, EditItem
from pccap.data.decode import greedy_decode
from pccap.harness.runs import run_stream
from pccap.routers import make_router


class Tokens:
    def encode(self, text):
        return np.int32([int(x) for x in text.split()])

    def decode(self, ids):
        return ' '.join(str(int(x)) for x in ids)


class SequentialTinyEvaluator(SupplementalEvaluator):
    # Avoid GPT-2 EOS padding on this deliberately 64-token model.
    def _decode_many(self, learner, prompts, tok):
        self.last_decodes = [greedy_decode(lambda ids: learner.predict(ids).logits, p, tok, max_new=1) for p in prompts]
        return self.last_decodes

    @staticmethod
    def _batch_last(learner, seqs, key_positions=None):
        return np.stack([learner.predict(ids).logits for ids in seqs])


def generate(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = {str(Path(__file__).relative_to(ROOT)):sha(__file__), 'aw/pc_v0.py':sha(ROOT/'aw/pc_v0.py')}
    manifest = output / 'synthetic-input.json'
    manifest.write_text(json.dumps({'ids':[4,11], 'target':17, 'tiny_fixture':True})+'\n')
    cells = [dict(dataset='zsre', realization=0, order=100, arm=arm, items=1) for arm in ('SE-A','SE-E')]
    (output/'plan.json').write_text(json.dumps(dict(population='cpu_smoke', cells=cells, sources=source)))
    for c in cells:
        out = output/f"zsre-r0-o100-{c['arm']}"
        out.mkdir()
        start = time.monotonic()
        base = TinyEPC()
        before = base.checksum(recompute=True)
        cap = Cap(base, CapConfig(d=base.d, arm='C1', credit='adjoint' if c['arm']=='SE-A' else 'error', credit_iters=8,
                                  radii={m:.5 for m in (1,2,3)}, bank_scales={m:1. for m in (1,2,3)}), base.ledger)
        cfg = dict(c, population='cpu_smoke', sources=source, weights_path=str(manifest), weights_sha256=sha(manifest),
                   manifest=str(manifest), manifest_sha256=sha(manifest), drift=dict(path=str(manifest),sha256=sha(manifest)),
                   initial_state=cap.state_hash(), item_ids=['synthetic-0'], locality_prompts_sha256=sha(manifest),
                   base_hash_before=before, error_lr=.1, credit_iters=8)
        (out/'config.json').write_text(json.dumps(cfg))
        item = EditItem(item_id='synthetic-0', digest=b'0'*16, prompt='4 11', answer='17', aliases=['17'],
                        paraphrases=['4 12'], locality_prompts=[], prompt_ids=np.int32([4,11]), answer_ids=np.int32([17]), dataset='tiny')
        ev = SequentialTinyEvaluator(base, Tokens(), [], None, max_new=1, secondary_path=out/'secondary.jsonl')
        metrics = run_stream(cap, [item], make_router('C1'), Budget(R=1,A=.3), ev, out, base.ledger, checkpoints=(), arm=c['arm'])
        vals = ev.last_items
        immediate = json.loads((out/'items.jsonl').read_text())
        secondary = dict(bounded_es_immediate=immediate['bounded_es'], bounded_ret_es_end=vals[0]['bounded_es'],
                         bounded_ret_gs_end=vals[0]['bounded_gs'], bounded_ls_end=None, items_completed=1,items_planned=1)
        (out/'secondary-summary.json').write_text(json.dumps(secondary))
        finish = dict(status=metrics['status'], dataset='zsre', arm=c['arm'],items_completed=1,items_planned=1,
                      base_hash_before=before, base_hash_after=base.checksum(recompute=True),
                      elapsed_process_seconds=time.monotonic()-start,ledger=base.ledger.totals())
        (out/'finish.json').write_text(json.dumps(finish))
        if c['arm']=='SE-E':
            diagnostics = credit_diagnostics(base,np.int32([4,11]),17,[])
            (output/'tiny-diagnostic.json').write_text(json.dumps(diagnostics))
    return output


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True)
    print(generate(p.parse_args().output))
