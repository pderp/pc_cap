# PC-6 — fixed-v5 checkpoint and harm-readout adapter

Capex, 2026-09-26. **Assigned CPU lane complete.** Production GPU integration and
execution belong to Capstan, held until Monday 09:00 per lead queue 120.

`aw/pc_v1_readout.py` restores either adjoint or error-credit `PCRevisionCap`
from its supplemental checkpoint, verifying file/state, original base, reader
weights and credit configuration. Wrong-arm checkpoints are refused; error
checkpoints retain the corrected SD-24 configuration and eight-step inference
metadata. The caller supplies the original fixed-v5 BP tensors through `EPCBase`,
not the regenerated ePC weights used by PC-v0.

Inference uses a separate, normally constructed **exact `RevisionCap`** with
identical weights, memory and inference configuration. Only acquisition-credit
metadata is omitted from this in-memory view. The checkpoint and original cap
are unchanged. The subclass's query methods must remain the inherited registered
methods; the frozen `PositionBatchReader` still rejects `PCRevisionCap` itself.
There is no class spoofing, monkeypatch or frozen-source edit.

The adapter exposes `adapter`, `batch_size`, `last_logits_batch`, `last_capoff`
and `events`, directly consumable by PC-5 `read_arm`. The unchanged registered
batch kernel shares the base pass with selection and retains its physical-padding
accounting. Source/view memory and reader identities are checked at assay
boundaries. Failed base work not already in the reader events is retained in the
failed readout cost; queries reset their inference cache.

Owner integration (variables below come from the completed supplemental run;
these are not proposed new resource paths):

```python
from aw.pc_v1_readout import PCPositionBatchReader
from aw.pc_harm_readout import selection, read_arm, pair

# binding: path, sha256, state_sha256, base_sha256, reader_sha256,
#          credit ('adjoint' or 'error'), iters (8)
reader = PCPositionBatchReader.from_checkpoint(
    base, cfg, reader_params, binding, batch_size=16
)
windows, population = selection("v5")  # 245,237 preselected positions
arm_result = read_arm(reader, windows, population, new_arm_output)
# After both arms: pair(adjoint_result, error_result, new_pair_npz)
```

The outer owner driver supplies the exclusive GPU lease, October 9 cutoff,
completion checks and shared readout allowance. This adapter does not dispatch
a model job or manage the global budget. PC-5's eight-hour ceiling is shared
across v0, fixed-v5 and readout reruns, not granted anew to this adapter.

Validation:

- Both modes: actual tiny-solver acquisition, checkpoint save/restore, bitwise
  ordinary-reader parity, six-position PC-5 harm assay, strict mode/base/file
  checks and mutation detection. A failed-batch fixture retains cost exactly
  once and publishes no successful vectors.
- Saved PC-4 GPT-2 development checkpoint: **ten prefixes match the registered
  batch reader bit for bit for both cap and base logits**. One prefix selects
  an active correction and changes logits; the others exercise the null gate.
  Selections and checkpoint/reader/base identities match. Batch size is two.
- Evidence: `results/additional_work/PC-6/devcheckpoint-verified.json` and
  `logs/additional_work/round47/pc6-verified-tests.txt`. Earlier `devcheckpoint`
  and `devcheckpoint-final` records are intermediate validation snapshots.

The real-base fixture copies a saved development state into an adjoint-mode
supplemental checkpoint. It establishes adapter parity, not new efficacy,
GPU parity/timing, or full 245,237-position coverage. Actual error acquisition
and restoration are covered by the tiny fixture; Monday's real experimental
error-mode checkpoint remains an owner integration check.
