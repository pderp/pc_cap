"""S1-04: P4 separability and useful sharing on the replacement grammar (plan §6.7 S1-04; PDF D.4).

D.4 asks for **error vectors**: for each mechanism and layer, 8,192 settled ePC error vectors from a
disjoint sample, centred, top-r orthonormal basis (r = 16 only if the spectrum supports it), the overlap
matrix ``O_ab = r⁻¹ ‖Uaᵀ Ub‖²_F``, captured variance, eigenvalue gaps and resampling stability; on the
synthetic fixture also private/private overlap for independent mechanisms, shared-component retention and
held-out compositional transfer. The natural-language domain PCA is ``unsupported`` (DATA-04).

Errors: the declared solver of S0-06 (simultaneous SGD on the error variables, ``error_lr = 0.1``, 8
iterations, CE on the designated target) run on the grammar base's weights through the FabricPC graph
(``pccap.pc.epc_inference.relax_errors``; the grammar has no ePC-trained twin, so these are "errors of the
declared solver on BP weights", the same label as the P6 BP-weights row). Sequences are task-switched
(the mechanism the base must learn), so the error field carries each mechanism's learning signal; the
evaluated position's error at every block output is the vector. A residual-vector PCA at the same
positions is reported alongside as a descriptive companion (Codex's handoff note), never as P4.

    JAX_PLATFORMS=cpu python -m pccap.analysis.s1_p4 [--n 8192] → results/S1/P4_gram.json, coverage row
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.contracts import metric
from pccap.fixtures.grammar_generator import CONTEXTS, KINDS, Grammar, Switches
from pccap.fixtures.grammar_model import CFG, WEIGHTS, GrammarBase
from pccap.metrics.overlap import subspace_overlap
from pccap.pc import epc_inference as epc
from pccap.pc.nodes import build_gpt2_graph, graph_params_from_numpy, node_names

ROOT = Path(__file__).resolve().parents[3]
S1 = ROOT / "results" / "S1"
R_TARGET = 16
ITERS, LR = 8, 0.1


def _batch(gr: Grammar, kind: str, contexts: list[int], seeds: np.ndarray, sw_fn) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ids = np.zeros((len(seeds), CFG.n_pos), np.int32)
    pos = np.zeros(len(seeds), np.int32)
    tgt = np.zeros(len(seeds), np.int32)
    for i, s in enumerate(seeds):
        c = contexts[i % len(contexts)]
        toks, p, _ = gr.sequence(c, sw_fn(c), int(s), kind)
        ids[i, :p] = toks[:p]
        pos[i], tgt[i] = p - 1, int(toks[p])
    return ids, pos, tgt


class ErrorSampler:
    """Settled error vectors (and residuals) at the evaluated position for every block output."""

    def __init__(self, base: GrammarBase, batch: int = 64):
        self.base, self.batch = base, batch
        self.structure = build_gpt2_graph(CFG, CFG.n_pos, epc.EPCInference(LR, ITERS))
        self.gp = graph_params_from_numpy(jax.tree_util.tree_map(np.asarray, base.params), CFG)
        self.names = node_names(CFG.n_layer)
        self._relax = jax.jit(lambda gp, cl: epc.relax_errors(gp, self.structure, cl, None, None, ITERS, LR))

        @jax.jit
        def residuals(params, ids):
            def one(i):
                h = g.embed(params, i)
                outs = []
                for l in range(CFG.n_layer):
                    h = g.block(params["blocks"][l], h, CFG)
                    outs.append(h)
                return jnp.stack(outs)  # [L, T, d]

            return jax.vmap(one)(ids)

        self._res = residuals

    def sample(self, ids: np.ndarray, pos: np.ndarray, tgt: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """→ errors [N, L, d], residuals [N, L, d] at the evaluated positions."""
        errs, ress = [], []
        for k in range(0, len(ids), self.batch):
            i, p, t = ids[k: k + self.batch], pos[k: k + self.batch], tgt[k: k + self.batch]
            y = np.zeros((len(i), CFG.n_pos, CFG.vocab), np.float32)
            y[np.arange(len(i)), p, t] = 1.0
            clamps = {self.names["ids"]: jnp.asarray(i), self.names["logits"]: jnp.asarray(y)}
            _, errors, _, _, _ = self._relax(self.gp, clamps)
            e = np.stack([np.asarray(errors[n]) for n in self.names["blocks"]], axis=1)  # [B, L, T, d]
            r = np.asarray(self._res(self.base.params, jnp.asarray(i)))  # [B, L, T, d]
            errs.append(e[np.arange(len(i)), :, p])
            ress.append(r[np.arange(len(i)), :, p])
        return np.concatenate(errs), np.concatenate(ress)


def basis(X: np.ndarray, r: int = R_TARGET) -> dict:
    """Centred top-r orthonormal basis with captured variance and eigen gaps; r is reduced when the spectrum does
    not support it (a relative eigenvalue below 1e-6 inside the top r → insufficient rank, labelled)."""
    Xc = X - X.mean(0, keepdims=True)
    U, S, Vt = np.linalg.svd(Xc.astype(np.float64), full_matrices=False)
    ev = S**2 / max(1, Xc.shape[0] - 1)
    tot = float(ev.sum())
    supported = int(np.sum(ev / max(tot, 1e-30) > 1e-6))
    r_eff = min(r, supported)
    return {"basis": Vt[:r_eff].T, "r": r_eff, "insufficient_rank": r_eff < r, "captured_variance": float(ev[:r_eff].sum() / tot) if tot else 0.0,
            "eigen_gaps": (ev[:r_eff] - np.append(ev[1:r_eff + 1], 0.0)[:r_eff]).tolist(), "eigenvalues": ev[: r + 4].tolist()}


def overlap(Ua: np.ndarray, Ub: np.ndarray) -> float:
    r = min(Ua.shape[1], Ub.shape[1])
    return float(subspace_overlap(Ua[:, :r], Ub[:, :r])["value"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8192)
    ap.add_argument("--batch", type=int, default=64)
    args = ap.parse_args(argv)
    t0 = time.time()
    gr = Grammar()
    base = GrammarBase(weights=WEIGHTS)
    sampler = ErrorSampler(base, args.batch)
    n = args.n
    L = CFG.n_layer
    out = {"stage": "S1", "property": "P4", "base": "GRAM (replacement grammar, BP weights)", "weights": base.checksum(),
           "solver": {"errors": "declared ePC solver on BP weights: SGD on error variables, lr 0.1, 8 iterations, CE on the designated target", "label": "errors of the declared solver on BP weights (no ePC-trained grammar)"},
           "n_per_set": n, "r_target": R_TARGET, "layers": L, "metrics": {}, "per_layer": {}}
    # 1. per mechanism (task-switched sequences, all contexts), disjoint seed blocks per kind and per half (resampling)
    sets = {}
    for ki, kind in enumerate(KINDS):
        seeds = 1_000_000 + 100_000 * ki + np.arange(n)
        ids, pos, tgt = _batch(gr, kind, list(range(CONTEXTS)), seeds, Switches.task)
        E, Rz = sampler.sample(ids, pos, tgt)
        sets[kind] = (E, Rz)
    # 2. private per context (private mechanism of context c only), 2,048 each, for private/private overlap
    priv = {}
    for c in range(CONTEXTS):
        seeds = 2_000_000 + 10_000 * c + np.arange(2048)
        ids, pos, tgt = _batch(gr, "private", [c], seeds, Switches.task)
        priv[c] = sampler.sample(ids, pos, tgt)[0]
    # 3. shared retention: shared_1 in contexts 0-3 vs 4-7 (same mechanism, disjoint contexts)
    sh = {}
    for tag, ctxs in (("A", [0, 1, 2, 3]), ("B", [4, 5, 6, 7])):
        seeds = 3_000_000 + (0 if tag == "A" else 50_000) + np.arange(4096)
        ids, pos, tgt = _batch(gr, "shared_1", ctxs, seeds, Switches.task)
        sh[tag] = sampler.sample(ids, pos, tgt)[0]
    # 4. held-out combinations (private-only / shared-only flips) for compositional transfer
    ho = {}
    for which in ("private_only", "shared_only"):
        seeds = 4_000_000 + (0 if which == "private_only" else 50_000) + np.arange(2048)
        kind = "private" if which == "private_only" else "shared_1"
        ids, pos, tgt = _batch(gr, kind, list(range(CONTEXTS)), seeds, lambda c, w=which: Switches.heldout(c, w))
        ho[which] = sampler.sample(ids, pos, tgt)[0]
    for layer in range(L):
        row = {"error": {}, "residual": {}}
        for space, idx in (("error", 0), ("residual", 1)):
            bases = {kind: basis(sets[kind][idx][:, layer]) for kind in KINDS}
            halves = {kind: (basis(sets[kind][idx][: n // 2, layer]), basis(sets[kind][idx][n // 2:, layer])) for kind in KINDS}
            O = {a: {b: overlap(bases[a]["basis"], bases[b]["basis"]) for b in KINDS} for a in KINDS}
            stab = {kind: overlap(halves[kind][0]["basis"], halves[kind][1]["basis"]) for kind in KINDS}
            row[space] = {"overlap": O, "captured_variance": {k: bases[k]["captured_variance"] for k in KINDS}, "r": {k: bases[k]["r"] for k in KINDS},
                          "insufficient_rank": {k: bases[k]["insufficient_rank"] for k in KINDS}, "eigen_gaps": {k: bases[k]["eigen_gaps"][:4] for k in KINDS},
                          "resampling_stability": stab}
        # fixture-specific (error space): private/private across contexts, shared retention, held-out transfer
        pb = {c: basis(priv[c][:, layer]) for c in range(CONTEXTS)}
        pp = [overlap(pb[a]["basis"], pb[b]["basis"]) for a in range(CONTEXTS) for b in range(a + 1, CONTEXTS)]
        sA, sB = basis(sh["A"][:, layer]), basis(sh["B"][:, layer])
        priv_all = basis(sets["private"][0][:, layer])
        sh1_all = basis(sets["shared_1"][0][:, layer])

        def captured(U, X):
            Xc = X - X.mean(0, keepdims=True)
            return float(np.sum((Xc @ U) ** 2) / max(np.sum(Xc**2), 1e-30))

        row["fixture"] = {"private_private_overlap_mean": float(np.mean(pp)), "private_private_overlap_max": float(np.max(pp)),
                          "shared_retention_overlap_ctxA_vs_ctxB": overlap(sA["basis"], sB["basis"]),
                          "heldout_transfer_private_basis_captures_private_only_flip": captured(priv_all["basis"], ho["private_only"][:, layer]),
                          "heldout_transfer_shared_basis_captures_shared_only_flip": captured(sh1_all["basis"], ho["shared_only"][:, layer]),
                          # cross-basis references: how much of each held-out flip the *other* kind's basis captures (a low effective
                          # rank makes any r-basis capture a lot; the difference to the own-basis value is the informative part)
                          "cross_capture_shared_basis_on_private_only_flip": captured(sh1_all["basis"], ho["private_only"][:, layer]),
                          "cross_capture_private_basis_on_shared_only_flip": captured(priv_all["basis"], ho["shared_only"][:, layer]),
                          "private_basis_captured_variance_own": priv_all["captured_variance"]}
        out["per_layer"][str(layer)] = row
    # summary metrics (error space, mean over layers)
    def mean_over_layers(fn):
        return float(np.mean([fn(out["per_layer"][str(l_)]) for l_ in range(L)]))

    out["metrics"] = {
        "error_overlap_private_shared1_mean": metric(mean_over_layers(lambda r: r["error"]["overlap"]["private"]["shared_1"]), units="overlap", n=n),
        "error_overlap_private_shared2_mean": metric(mean_over_layers(lambda r: r["error"]["overlap"]["private"]["shared_2"]), units="overlap", n=n),
        "error_overlap_shared1_shared2_mean": metric(mean_over_layers(lambda r: r["error"]["overlap"]["shared_1"]["shared_2"]), units="overlap", n=n),
        "error_resampling_stability_min": metric(float(min(min(out["per_layer"][str(l_)]["error"]["resampling_stability"].values()) for l_ in range(L))), units="overlap", n=n),
        "error_captured_variance_r16_mean": metric(mean_over_layers(lambda r: float(np.mean(list(r["error"]["captured_variance"].values())))), units="fraction", n=n),
        "insufficient_rank_cases": metric(float(sum(sum(r["error"]["insufficient_rank"].values()) for r in out["per_layer"].values())), units="count", n=L * 3),
        "private_private_overlap_mean": metric(mean_over_layers(lambda r: r["fixture"]["private_private_overlap_mean"]), units="overlap", n=28 * L),
        "shared_retention_overlap_mean": metric(mean_over_layers(lambda r: r["fixture"]["shared_retention_overlap_ctxA_vs_ctxB"]), units="overlap", n=L),
        "heldout_transfer_private_mean": metric(mean_over_layers(lambda r: r["fixture"]["heldout_transfer_private_basis_captures_private_only_flip"]), units="fraction", n=L),
        "heldout_transfer_shared_mean": metric(mean_over_layers(lambda r: r["fixture"]["heldout_transfer_shared_basis_captures_shared_only_flip"]), units="fraction", n=L),
        "residual_overlap_private_shared1_mean": metric(mean_over_layers(lambda r: r["residual"]["overlap"]["private"]["shared_1"]), units="overlap", n=n, status="ok"),
        "cross_capture_shared_basis_on_private_only_flip_mean": metric(mean_over_layers(lambda r: r["fixture"]["cross_capture_shared_basis_on_private_only_flip"]), units="fraction", n=L),
        "cross_capture_private_basis_on_shared_only_flip_mean": metric(mean_over_layers(lambda r: r["fixture"]["cross_capture_private_basis_on_shared_only_flip"]), units="fraction", n=L),
        "chance_overlap_random_r_subspaces": metric(R_TARGET / CFG.d, units="overlap", n=0, status="ok"),
        "natural_language_domain_pca": metric(None, units="overlap", n=0, status="unsupported"),
    }
    out["notes"] = ["D.4 error-space P4 on the grammar; residual PCA is a descriptive companion (not P4)", "natural-language domain PCA unsupported (DATA-04)",
                    "any claim of private/shared structure requires the S3 intervention and transfer checks (D.4)"]
    out["seconds"] = time.time() - t0
    S1.mkdir(parents=True, exist_ok=True)
    (S1 / "P4_gram.json").write_text(json.dumps(out, indent=1, default=float))
    from pccap.analysis.s1_p6 import update_coverage

    update_coverage({"P4": {"gram_error": "complete (results/S1/P4_gram.json)", "gram_residual_companion": "complete (descriptive)", "natural_language": "unsupported (DATA-04)"}})
    print(json.dumps({k: v["value"] for k, v in out["metrics"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
