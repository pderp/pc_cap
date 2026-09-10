"""The pinned distillation recipe (sibling ``reproduction/experiments.json`` profile ``distillation``
and ``inputs.json``; commit 298fc719…). Nothing here is tunable for the regeneration: REG-02 must
run these settings. ``Recipe`` fields that are *ours* (micro-batch size, checkpoint cadence, log
paths) do not change the mathematics (micro-batching is exact, DEC-014)."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

from pccap import ASSETS_ROOT

SIBLING_COMMIT = "298fc719a0bb3e50a2b818990dd61ccca438ee62"

# --- data (inputs.json "sources.openwebtext" / "shards.openwebtext.bin")
OWT_REPO = "Skylion007/openwebtext"
OWT_REVISION = "b4325f019c648b1641a1784748667e8b74e5e064"
OWT_FILE = "plain_text/train-00000-of-00080.parquet"
OWT_PARQUET_SHA256 = "caed9f4b7053d7cd4d1a13ce9ec9224d84a3bba1f11579193562a7e31ebe656e"
OWT_TOKENS = 52_500_000
OWT_SHARD_SHA256 = "ae5b795aadcd3ef8990826c1ef37661b53b216e962e3bec8510a8758fecf540d"
PROBES_TOKENS = 903
PROBES_SHA256 = "b57f1306c262dc70ea2c9cb91794089a1370d7f9a91b7ddb765063226bb57878"
DOCS_PER_BATCH = 256  # tokenizer batch in the sibling's build_shards (order-preserving; no effect on bytes)

OWT_DIR = Path(ASSETS_ROOT) / "data" / "raw" / "openwebtext"
SHARD_PATH = OWT_DIR / "openwebtext.bin"
PROBES_PATH = OWT_DIR / "distillation-probes.bin"
RUNS_DIR = Path(ASSETS_ROOT) / "models" / "epc"

# --- sibling monitor constants (hdpc/train_distill.py:76-78, homotopy.py:44-48)
MAX_SUBDIVISIONS_PER_RUNG = 2
RELAXATION_DIVERGENCE_THRESHOLD = 1.05
RELAXATION_DIVERGENCE_STEPS = 20
HOLD_HEADROOM_FRACTION = 0.5
HOLD_ABSOLUTE_THRESHOLD = 1.02

# hdpc/train_distill.py:80-101 (prompt-KL milestone / abort rule)
EVAL_PROMPTS = [
    "The model predicts the next token from the prior context.",
    "A stable training path should keep teacher and student close.",
    "Residual stream states are compared at block boundaries.",
    "The energy decreases when error variables move downhill.",
    "Short prompts make the smoke run cheap and repeatable.",
    "Language models assign probability to every vocabulary item.",
    "The hidden state is a sequence of vectors.",
    "Distillation uses a frozen teacher distribution.",
    "A causal mask prevents attention to future positions.",
    "The optimizer should not see error gradients during relaxation.",
    "Temperature changes the scale of the soft targets.",
    "A tracking residual can pause a schedule.",
    "The checkpoint is loaded by its full repository id.",
    "Dropout is disabled while gradients are still tracked.",
    "The readout weight is tied to the input embedding.",
    "Layerwise cosines compare two gradient fields.",
    "A synthetic token stream avoids dataset downloads.",
    "Every relaxation step is a full prefill pass.",
    "Small batches fit the local graphics card.",
    "The smoke run is not the full annealing run.",
]


@dataclasses.dataclass(frozen=True)
class Recipe:
    # protocol (experiments.json "distillation" args) — do not change
    seq_len: int = 512
    batch_size: int = 10
    seed: int = 1729
    token_budget: int = 50_000_000
    error_lr: float = 0.1
    tau_max: float = 6.4  # schedule [1, 2, 4, 8, 16, 32, 64]
    weight_lr: float = 1e-6
    weight_decay: float = 0.0
    adam_betas: tuple[float, float] = (0.9, 0.999)
    adam_eps: float = 1e-8
    kd_temperature: float = 2.0
    milestone_tokens: int = 1_000_000
    eval_seq_len: int = 32
    eval_batch_size: int = 1
    eval_batches: int = 3
    eval_start_index: int = 0
    kl_abort_threshold: float = 0.05
    hold_ema_decay: float = 0.99
    hold_window_steps: int = 64
    hold_energy_floor: float = 1e-9
    hold_patience_steps: int = 100
    # ours (no effect on the mathematics)
    micro_batch_size: int = 5
    checkpoint_every: int = 250
    keep_last_k: int = 3
    heldout_windows: int = 64  # extra fidelity probe on the untouched tail tokens[training_tokens:]

    @property
    def tokens_per_step(self) -> int:
        return self.seq_len * self.batch_size

    @property
    def total_steps(self) -> int:
        # hdpc/train_distill.py:1117-1121
        return -(-self.token_budget // self.tokens_per_step)

    @property
    def training_tokens(self) -> int:
        return self.total_steps * self.tokens_per_step  # 50,001,920: the last token position the run reads

    def schedule(self) -> list[int]:
        # hdpc/train_distill.py:1102-1114 (schedule_from_args with tau_max)
        target = max(1, int(round(self.tau_max / self.error_lr)))
        steps, value = [], 1
        while value < target:
            steps.append(value)
            value *= 2
        steps.append(target)
        return steps

    def protocol_dict(self) -> dict:
        d = dataclasses.asdict(self)
        for k in ("micro_batch_size", "checkpoint_every", "keep_last_k", "heldout_windows"):
            d.pop(k)
        d["schedule"] = self.schedule()
        d["total_steps"] = self.total_steps
        return d

    def protocol_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.protocol_dict(), sort_keys=True).encode()).hexdigest()[:16]
