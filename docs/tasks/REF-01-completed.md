# REF-01 — completed CPU reference fixtures

status: complete for REF-01; downstream JAX/HF parity remains unverified by this lane
agent: codex
completed_utc: 2026-09-10T00:57:24.992479+00:00
worktree: `/home/derp/cap/pc_cap` (shared main tree)
commit: none; this lane did not stage, commit, merge, push, or create a worktree

This completion addendum supersedes the paused status in `docs/tasks/REF-01.md` without editing that historical record. The user approved the exact correction in `docs/tasks/REF-01-test-correction.patch`; it was applied only to `tests/reference/test_reference_fixtures.py`. All other writes in this continuation created new files. Shared task/status manifests and other agents' files were left to their owners.

Scope and source specification: REF-01 in `docs/ongoing2.md` and `docs/ongoing.md`, supporting the PDF-derived S0-04 and S0-09 checks. The pinned GPT-2 revision is `607a30d783dfa663caf39e06633721c8d4cfcd7e`. Model, tokenizer, and zsRE inputs were rehashed against DATA-00 before generation. Only the first 256 `src` prompts were used; answer fields did not affect selection, inference, or saved prompt inventory.

## Deliverables and checkpoint results

1. Separate CPU reference environment exists at `/home/derp/cap/assets/envs/ref-torch-cpu`. Python 3.12.14, torch 2.11.0+cpu, Transformers 5.13.1, and NumPy 2.5.3; the full package inventory is in `assets/reference/gpt2/ref_env.json`. The existing JAX/FabricPC environment and both read-only reference repositories were not modified by this lane.
2. `scripts/make_reference_fixtures.py` loads the local checkpoint in fp32/eval/eager mode with deterministic algorithms enabled, four CPU intra-op threads and one inter-op thread. It never overwrites an existing artifact or manifest. Full archives are streamed one array at a time to keep memory bounded.
3. `logits_256.npz` contains 256 tokenized prompts (2,802 token positions), full `[T, 50257]` fp32 logits, post-block `[T, 768]` residuals at blocks 3, 7, and 11, plus separate post-`ln_f` arrays. Block 11 is captured before final layer normalization. Each prompt has an item ID, source index, prompt-text hash, and token count in `manifests/reference.json`. HF encoding agreed with the local raw `tokenizer.json` encoding for every prompt.
4. `greedy_8.json` records deterministic HF generation with and without KV caching for the first eight prompts, at most 32 new tokens, EOS stopping. **8/8 cached and uncached sequences match exactly.** These are raw HF continuations; the existing project decoder may stop at newline and compares its generated prefix.
5. `lengths.npz` contains token IDs and logits for lengths 1, 2, 3, 5, 8, 16, 64, and 128, generated with NumPy seed 0.
6. `ref_env.json` records execution settings, CPU model, package versions, timing, and the other artifact hashes. `manifests/reference.json` hashes all four artifacts, including `ref_env.json`, and records source and generator hashes.
7. All eight CPU controls passed after the approved test edit; Ruff passed. The correction checks our hook cleanup before Transformers installs its own persistent output-capture hooks, then checks that another capture preserves those existing third-party hooks. The model-output comparisons required no change.
8. Generation's final reload/hash check passed. A separate `--check` invocation from the existing project venv also passed, requiring NumPy only. Checks cover artifact hashes and byte sizes, immutable input hashes, prompt and array inventory, fp32 shapes and finite values, deterministic length inputs, and greedy sequence consistency.

The artifacts total 643,762,838 bytes and are all outside the repository at `/home/derp/cap/assets/reference/gpt2/`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `logits_256.npz` | 598,112,256 | `5fcaf4c611e5aadbd43936f381aabef993ee19b804befa31068885aa14c12f3c` |
| `lengths.npz` | 45,638,500 | `9d16a1be6504c6a0879366add38647ce91c3cd67163fcf8cf9e044cb1a71d74b` |
| `greedy_8.json` | 9,857 | `43174ccf1a7a40521ac44086ec29518657a25fea70d9fcdd3645f4188084ecc5` |
| `ref_env.json` | 2,225 | `8cb9086dce6ce6c61d550a5b3fb215dfda38dfa3a4daac9a7098b80dc3e225da` |

## Validation and cost

Executed from `/home/derp/cap/pc_cap`:

```bash
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' /home/derp/cap/assets/envs/ref-torch-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/reference/test_reference_fixtures.py --basetemp=/home/derp/cap/assets/tmp/ref01/pytest-controls-approved
/home/derp/cap/venv/bin/ruff check --no-cache scripts/make_reference_fixtures.py tests/reference/test_reference_fixtures.py
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' TMPDIR=/home/derp/cap/assets/tmp/ref01 /home/derp/cap/assets/envs/ref-torch-cpu/bin/python -B scripts/make_reference_fixtures.py --threads 4
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' /home/derp/cap/venv/bin/python -B scripts/make_reference_fixtures.py --check
```

Results: **8 passed in 3.76 seconds**, lint clean, generation verified, independent recheck verified. The generation command intentionally refuses a repeat at the same output paths; use `--check` for existing artifacts. Repeating pytest should use a fresh `--basetemp` path to preserve earlier temporary fixtures.

Recorded generator wall time through artifact hashing: **20.419 seconds** (excludes environment setup and final validation); CPU: AMD Ryzen 7 9700F 8-Core Processor; **gpu_seconds = 0**; no GPU lease used. Logs: `results/REF-01/verification_attempt_2.txt`, `results/REF-01/generation.txt`, and `results/REF-01/verification_check.txt`. The first failed test log and hook diagnostic are retained as the history behind the approved correction.

## Files for review and handoff

Created across this REF-01 effort:

- `scripts/make_reference_fixtures.py`
- `tests/reference/test_reference_fixtures.py` (subsequently changed by the single approved patch)
- `manifests/reference.json`
- `docs/tasks/REF-01.claim.json`
- `docs/tasks/REF-01.md`
- `docs/tasks/REF-01-test-correction.patch`
- `docs/tasks/REF-01-completed.md`
- `results/REF-01/hook_diagnostic.json`
- `results/REF-01/verification_attempt_1.txt`
- `results/REF-01/verification_attempt_2.txt`
- `results/REF-01/generation.txt`
- `results/REF-01/verification_check.txt`

External additions: the isolated CPU environment, the four reference artifacts above, and temporary dependency/test resources under `assets/tmp/ref01/`. This list is scoped to this lane; other uncommitted files belong to concurrently working agents.

The S0 owner can now consume the artifacts through the existing `tests/bases/test_bp_base.py::test_a_hf_oracle` and `tests/data/test_decode.py::test_bp_decode_vs_hf_oracle` paths. Those comparisons were not run here: the S0 base test writes an existing shared control report, and the GPU is managed by the orchestrator. No JAX/HF tolerance, argmax, or scientific checkpoint claim follows from fixture generation alone. The synthetic-length oracle is available for the S0-04(f) owner to consume. Shared board updates and S0 report changes belong to that owner under the user's existing-file edit rule.

Parallelism: artifact verification is CPU-only and read-only and can run alongside the orchestrator's S1/S2 work. The S0 comparisons can be scheduled by the S0 owner using the existing GPU coordination rules. This lane is complete and holds no GPU lease or running process.
