"""Exact small-matrix controls for optional shadow diagnostics (PDF D.9).

These functions operate on fixed finite matrices, not the actual discrete cap
update. They provide control oracles for a later JAX HVP implementation; no
HVP sweep, checkpoint loading, inference or GPU work happens here.
"""

import numpy as np

from pccap.contracts import metric


def _square(matrix):
    a = np.asarray(matrix, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or len(a) == 0 or not np.isfinite(a).all():
        raise ValueError("expected a finite nonempty square matrix")
    return a


def commutator(h_i, h_j):
    """C_ij = H_i H_j - H_j H_i for two symmetric task-loss Hessians."""
    a, b = _square(h_i), _square(h_j)
    if a.shape != b.shape:
        raise ValueError("Hessians must have the same shape")
    if not np.allclose(a, a.T, atol=1e-12, rtol=0) or not np.allclose(b, b.T, atol=1e-12, rtol=0):
        raise ValueError("Hessians must be symmetric")
    return a @ b - b @ a


def commutator_gram(commutators):
    """G_ab = Tr(C_a.T C_b), not Tr(C_a C_b); this is positive semidefinite."""
    matrices = [_square(c) for c in commutators]
    if not matrices or any(c.shape != matrices[0].shape for c in matrices):
        raise ValueError("at least one same-shaped commutator is required")
    flat = np.stack([c.reshape(-1) for c in matrices])
    return flat @ flat.T


def linearized_loop(h_i, h_j, eta: float):
    """A_j^-1 A_i^-1 A_j A_i for A_i=I-eta*H_i; limit I-eta²*C_ij.

    A linearized inverse exists only for nonsingular A_i/A_j. It is never an
    inverse of the actual allocation/eviction learner update.
    """
    # Validate the Hessian coordinates and symmetry even at eta=0.
    commutator(h_i, h_j)
    if not np.isfinite(eta) or eta < 0:
        raise ValueError("eta must be finite and nonnegative")
    h_i, h_j = _square(h_i), _square(h_j)
    identity = np.eye(len(h_i))
    a_i, a_j = identity - eta * h_i, identity - eta * h_j
    try:
        return np.linalg.solve(a_j, np.linalg.solve(a_i, a_j @ a_i))
    except np.linalg.LinAlgError as error:
        raise ValueError("linearized maps must be invertible") from error


def block_accounting(operator, projectors):
    """Full-operator block masses, including m != n cross-bank contributions."""
    c = _square(operator)
    blocks = [_square(p) for p in projectors]
    if not blocks or any(p.shape != c.shape for p in blocks):
        raise ValueError("projectors must match the operator shape")
    for i, p in enumerate(blocks):
        if not np.allclose(p, p.T, atol=1e-12, rtol=0) or not np.allclose(
            p @ p, p, atol=1e-12, rtol=0
        ):
            raise ValueError("each projector must be orthogonal and idempotent")
        for q in blocks[:i]:
            if not np.allclose(p @ q, 0, atol=1e-12, rtol=0):
                raise ValueError("projectors must have mutually orthogonal ranges")
    if not np.allclose(np.sum(blocks, axis=0), np.eye(len(c)), atol=1e-12, rtol=0):
        raise ValueError("projectors must partition the entire parameter space")
    mass = np.array([[np.sum((p @ c @ q) ** 2) for q in blocks] for p in blocks])
    full = float(np.sum(c**2))
    parts = float(mass.sum())
    return {
        "full_squared_frobenius": metric(
            full, units="squared_operator_norm", numerator=full, denominator=1, n=c.size
        ),
        "sum_block_squared_frobenius": metric(
            parts, units="squared_operator_norm", numerator=parts, denominator=1, n=mass.size
        ),
        "block_squared_frobenius": mass.tolist(),
        "cross_block_squared_frobenius": float(parts - np.trace(mass)),
        "residual": float(parts - full),
    }


def control_fixture():
    """Fixed 4x4 integer-valued Hessians and two coordinate-block projectors."""
    h_i = np.diag([1.0, 2.0, 3.0, 4.0])
    h_j = np.array(
        [[2.0, 1.0, 1.0, 0.0], [1.0, 3.0, 0.0, 1.0], [1.0, 0.0, 4.0, 1.0], [0.0, 1.0, 1.0, 5.0]]
    )
    h_k = np.array(
        [[4.0, 0.0, 2.0, 0.0], [0.0, 2.0, 1.0, 1.0], [2.0, 1.0, 5.0, 0.0], [0.0, 1.0, 0.0, 3.0]]
    )
    projectors = [np.diag([1.0, 1.0, 0.0, 0.0]), np.diag([0.0, 0.0, 1.0, 1.0])]
    return h_i, h_j, h_k, projectors


def run_controls():
    """JSON-safe observed controls; failures are visible in pass fields."""
    h_i, h_j, h_k, projectors = control_fixture()
    comms = [commutator(h_i, h_j), commutator(h_i, h_k), commutator(h_j, h_k)]
    gram = commutator_gram(comms)
    eigenvalues = np.linalg.eigvalsh(gram)
    negative_trace = np.array([[-np.trace(a @ b) for b in comms] for a in comms])
    loop_rows = []
    for eta in (0.001, 0.0005):
        loop = linearized_loop(h_i, h_j, eta)
        correct = float(np.linalg.norm(loop - np.eye(4) + eta**2 * comms[0]))
        wrong = float(np.linalg.norm(loop - np.eye(4) - eta**2 * comms[0]))
        loop_rows.append(
            {"eta": eta, "correct_sign_remainder": correct, "wrong_sign_remainder": wrong}
        )
    reduction = loop_rows[0]["correct_sign_remainder"] / loop_rows[1]["correct_sign_remainder"]
    block = block_accounting(comms[0], projectors)
    checks = {
        "antisymmetry": all(np.array_equal(c.T, -c) for c in comms),
        "gram_sign": bool(np.array_equal(gram, negative_trace)),
        "gram_psd": bool(eigenvalues.min() >= -1e-10),
        "loop_sign": all(
            row["correct_sign_remainder"] < row["wrong_sign_remainder"] for row in loop_rows
        ),
        "loop_cubic_remainder": bool(7.5 < reduction < 8.5),
        "full_block_identity": abs(block["residual"]) <= 1e-12,
        "nonzero_cross_blocks": block["cross_block_squared_frobenius"] > 0,
    }
    return {
        "fixture": "fixed_4x4_integer_hessians",
        "scope": "small-matrix controls only",
        "passed": all(checks.values()),
        "checks": checks,
        "gram": gram.tolist(),
        "gram_eigenvalues": eigenvalues.tolist(),
        "loop": loop_rows,
        "remainder_reduction_on_halving_eta": reduction,
        "block_accounting": block,
    }
