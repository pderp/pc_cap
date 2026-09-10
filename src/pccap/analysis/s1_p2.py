"""S1-02: P2 geometry and non-collapse (PDF D.2; plan §6.7).

Per layer boundary (embedding output and the 12 block outputs, i.e. the residual stream before
each block and before ``ln_f``): effective rank of the centred hidden features at the 4,096 P2
positions (full singular spectrum stored), and a fixed linear part-of-speech probe (multinomial
logistic regression, ``optax.adam``, fixed steps and seed) trained on the UD-EWT train first-
sub-token features and evaluated on the disjoint dev set, matched across bases. Ratios to the
teacher apply when an ePC checkpoint exists; alerts (rank ratio < 0.9, probe drop > 0.02) are
alerts only. BP rows now; ePC rows pending REG-03.

    python -m pccap.analysis.s1_p2      # GPU lease
→ results/S1/P2_bp.json, results/S1/coverage.json (P2 row).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import optax

from pccap.bases import gpt2_jax as _g
from pccap.bases.bp import BPBase
from pccap.contracts import metric
from pccap.harness.ledger import Ledger
from pccap.metrics.rank import effective_rank

ROOT = Path(__file__).resolve().parents[3]
LM_MANIFEST = ROOT / "manifests" / "dev" / "lm_sets.json"
S1 = ROOT / "results" / "S1"
PROBE_STEPS, PROBE_LR, PROBE_SEED = 400, 1e-2, 0
N_LAYERS = 13


def _load(name: str) -> np.ndarray:
    inv = json.loads(LM_MANIFEST.read_text())
    return np.load(inv["files"][name]["path"])


def hidden_at_positions(base: BPBase, seqs: np.ndarray, positions: np.ndarray, batch: int = 32) -> np.ndarray:
    """``[n_layers, N_positions, d]`` hidden features at the given positions of every sequence."""
    feats = []
    for i in range(0, len(seqs), batch):
        hs = base.all_hidden_batch(seqs[i : i + batch])  # [B, 13, T, d]
        feats.append(hs[:, :, positions, :].reshape(hs.shape[0], N_LAYERS, len(positions), -1))
    f = np.concatenate(feats)  # [N_seq, 13, P, d]
    return f.transpose(1, 0, 2, 3).reshape(N_LAYERS, -1, f.shape[-1])


def pos_features(base: BPBase, ids: np.ndarray, labels: np.ndarray, sents: np.ndarray, max_tokens: int, T: int = 128) -> tuple[np.ndarray, np.ndarray]:
    """Hidden features (all layers) of labelled first sub-tokens, running sentences packed into
    T-token windows that never cross sentence boundaries (each window starts at a sentence start)."""
    feats, labs = [], []
    starts = np.flatnonzero(np.diff(np.concatenate([[-1], sents])) != 0)
    windows = []
    cur = []
    cur_len = 0
    for s_i, st in enumerate(starts):
        en = starts[s_i + 1] if s_i + 1 < len(starts) else len(ids)
        L = en - st
        if L > T:
            continue
        if cur_len + L > T:
            windows.append((cur, cur_len))
            cur, cur_len = [], 0
        cur.append((st, en))
        cur_len += L
    if cur:
        windows.append((cur, cur_len))
    total = 0
    batch_ids, batch_lab = [], []
    for spans, L in windows:
        seq = np.concatenate([ids[a:b] for a, b in spans])
        lab = np.concatenate([labels[a:b] for a, b in spans])
        pad = np.full(T - L, 50256, np.int32)
        batch_ids.append(np.concatenate([seq, pad]))
        batch_lab.append(np.concatenate([lab, np.full(T - L, -1, np.int32)]))
        total += int((lab >= 0).sum())
        if total >= max_tokens:
            break
    ids_arr = np.stack(batch_ids)
    lab_arr = np.stack(batch_lab)
    for i in range(0, len(ids_arr), 32):
        hs = base.all_hidden_batch(ids_arr[i : i + 32])  # [B, 13, T, d]
        m = lab_arr[i : i + 32] >= 0
        feats.append(hs.transpose(1, 0, 2, 3)[:, m])  # [13, n, d]
        labs.append(lab_arr[i : i + 32][m])
    return np.concatenate(feats, axis=1), np.concatenate(labs)


def linear_probe(x_tr: np.ndarray, y_tr: np.ndarray, x_ev: np.ndarray, y_ev: np.ndarray, n_classes: int, steps: int = PROBE_STEPS,
                 lr: float = PROBE_LR, seed: int = PROBE_SEED) -> dict:
    mu, sd = x_tr.mean(0), x_tr.std(0) + 1e-6
    xt = jnp.asarray((x_tr - mu) / sd)
    xe = jnp.asarray((x_ev - mu) / sd)
    yt = jnp.asarray(y_tr)
    key = jax.random.PRNGKey(seed)
    W = 0.01 * jax.random.normal(key, (x_tr.shape[1], n_classes), jnp.float32)
    b = jnp.zeros((n_classes,), jnp.float32)
    opt = optax.adam(lr)
    state = opt.init((W, b))

    def loss_fn(params):
        W, b = params
        lp = jax.nn.log_softmax(xt @ W + b, axis=-1)
        return -jnp.mean(jnp.take_along_axis(lp, yt[:, None], axis=-1))

    @jax.jit
    def step(params, state):
        loss, g = jax.value_and_grad(loss_fn)(params)
        upd, state = opt.update(g, state)
        return optax.apply_updates(params, upd), state, loss

    params = (W, b)
    for _ in range(steps):
        params, state, loss = step(params, state)
    W, b = params
    pred_tr = np.asarray(jnp.argmax(xt @ W + b, axis=-1))
    pred_ev = np.asarray(jnp.argmax(xe @ W + b, axis=-1))
    return {"train_acc": float((pred_tr == y_tr).mean()), "eval_acc": float((pred_ev == y_ev).mean()), "final_loss": float(loss),
            "n_train": int(len(y_tr)), "n_eval": int(len(y_ev)), "steps": steps, "lr": lr, "seed": seed}


def run(label: str = "bp", weights: str | None = None) -> dict:
    from pccap.harness.lease import gpu_lease

    S1.mkdir(parents=True, exist_ok=True)
    inv = json.loads(LM_MANIFEST.read_text())
    with gpu_lease("S1-02", stage="S1", projected_seconds=1800) as lease:
        ledger = Ledger()
        base = BPBase(ledger=ledger, params_np=(_g.load_params_npz(weights) if weights else None))
        P2 = _load("P2_sequences")
        pos = _load("P2_positions")
        feats = hidden_at_positions(base, P2, pos)  # [13, 4096, d]
        ranks = {}
        spectra = {}
        for l in range(N_LAYERS):
            X = feats[l].astype(np.float64)
            m = effective_rank(X)
            ranks[str(l)] = m
            s = np.linalg.svd(X - X.mean(0), compute_uv=False)
            spectra[str(l)] = s.tolist()
        tr_x, tr_y = pos_features(base, _load("POS_train_ids"), _load("POS_train_labels"), _load("POS_train_sentences"), 20000)
        ev_x, ev_y = pos_features(base, _load("POS_dev_ids"), _load("POS_dev_labels"), _load("POS_dev_sentences"), 5000)
        n_classes = len(inv["pos_train"]["upos"])
        probes = {str(l): linear_probe(tr_x[l], tr_y, ev_x[l], ev_y, n_classes) for l in range(N_LAYERS)}
        out = {
            "stage": "S1", "property": "P2", "base": label, "positions": int(feats.shape[1]), "layers": "0 = embedding output; l = output of block l-1 (pre-ln_f for 12)",
            "metrics": {**{f"effective_rank_layer{l}": ranks[str(l)] for l in range(N_LAYERS)},
                        **{f"pos_probe_acc_layer{l}": metric(probes[str(l)]["eval_acc"], units="accuracy", n=probes[str(l)]["n_eval"]) for l in range(N_LAYERS)}},
            "spectra": spectra, "probes": probes, "probe_definition": "multinomial logistic regression on standardized features, adam lr 1e-2, 400 steps, seed 0; train = UD-EWT train first sub-tokens, eval = UD-EWT dev (disjoint)",
            "alerts": {"rank_ratio_below_0.9": "n/a (single base)", "probe_drop_above_0.02": "n/a (single base)"},
            "teacher_ratios": "pending REG-03 (no ePC checkpoint)", "seeds": {"P2": inv["seeds"]["P2"], "probe": PROBE_SEED},
            "lease": lease.report, "ledger": ledger.totals(), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    (S1 / f"P2_{label}.json").write_text(json.dumps(out, indent=1, default=float))
    from pccap.analysis.s1_p6 import update_coverage

    update_coverage({"P2": ({"bp": "complete", "epc": "pending (REG-03)", "grammar": "pending (GRAM-02)"} if label != "epc" else {"epc": "complete (" + str(weights) + ")"})})
    return out


def _cli():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--epc-weights", default=None, help="regenerated ePC params.npz → writes the epc row (label 'epc')")
    a = ap.parse_args()
    return run("epc", a.epc_weights) if a.epc_weights else run()


if __name__ == "__main__":
    o = _cli()
    print({k: round(v["value"], 2) if v["value"] is not None else None for k, v in o["metrics"].items()})
