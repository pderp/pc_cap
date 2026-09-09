"""CPU float64 measurement functions; scalar results implement contracts.Metric."""

from .cl_matrix import acc, bwt, forgetting, fwt, late_acquisition_gain, summarize
from .divergence import js, kl
from .editing import exact_match_aliases, normalize_answer
from .order import damage, order_divergence, scalar_quadratic_reversal
from .overlap import subspace_overlap
from .participation import active_fraction, pr
from .rank import effective_rank

__all__ = [
    "acc",
    "active_fraction",
    "bwt",
    "damage",
    "effective_rank",
    "exact_match_aliases",
    "forgetting",
    "fwt",
    "js",
    "kl",
    "late_acquisition_gain",
    "normalize_answer",
    "order_divergence",
    "pr",
    "scalar_quadratic_reversal",
    "subspace_overlap",
    "summarize",
]
