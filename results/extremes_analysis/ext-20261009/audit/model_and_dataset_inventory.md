# Model and dataset inventory (Stage 1 audit)

Capstan · 9 October 2026 · read-only audit of the frozen record. Paths are relative to `/home/derp/cap/pc_cap` unless they start with `assets/`.

## 1. Research programme and architecture (what exists)

The pc_cap programme attaches a small *cap* to a frozen GPT-2 small. The cap reads the residual stream at three sites (after blocks 4, 8, 12; zero-based block indices 3, 7, 11) and can add one write vector per site at the current prediction position. A **memory** stores one record per taught fact (key = prompt embedding at the three taps; payload = per-answer-token write deltas, shape [3, 768]). A **reader** (3,348,228 parameters: tap encoder, tied query/key heads, code head, null head; controller bypassed by the delta rule) decides at query time whether any stored record applies (null mass ≥ 0.5 → no write → output equals the base to the bit). Writes are **episodic**: each edit is taught by five adjoint gradient steps on its own delta (A = 0.3 aggregate budget, τ = 0.1 acceptance), appended to the store; the reader weights are fixed during a stream. State carried across examples is the memory store only.

| item | value | source |
|---|---|---|
| frozen backbone | GPT-2 small, 12 blocks, d = 768, 12 heads, 124,439,808 params, tied `wte` head | `src/pccap/bases/gpt2_jax.py`; HF snapshot `assets/hf_cache/.../607a30d7…` |
| backbone identity | params digest `c4ac3fb8…` (sha256 over float32 named arrays); safetensors blob `248dfc39…` | `src/pccap/bases/bp.py:_digest`; every recipe `adapter_identity.base_sha256` |
| what is frozen | all base weights; cap reader weights during a stream; only the memory grows | `revision_v1/learner.py` |
| cap sites / interface | read taps [1,2,3], write sites [1,2,3] in every PCR arm (AW-L varied this separately) | `results/additional_work/PC-reader/eval-*/report.json: read_taps, write_sites` |
| reader config | width 256, d_code 256, top-k 4, cosine scores ×10, pairwise + query null, lexical term, null threshold 0.5, hard top-1 | `eval-*/stream/config.json: semantic_config` |
| acquisition | adjoint delta rule: 5 steps, lr 0.1, τ 0.1; A = 0.3; bank scales [70.70, 106.58, 425.57] | same |
| memory | append-only RecordStore, 64 MiB ceiling, binary mass | same |

### 1.1 The three principal models (amendment §2.A)

| model id | definition | checkpoint artifact | training |
|---|---|---|---|
| `frozen` | GPT-2 small, **no reader, no memory, no writes** | base params only | none |
| `bp_reader_s{0,1,2}` | same base + reader trained by backprop, seed s | `assets/runs/additional_work/PC-reader/train-bp-s{s}/theta_avg150-300.npz` (params sha in `train-bp-s{s}/report.json`) | 300 AdamW updates (lr 1e-3, wd 0.01, clip 1.0), batch 2, 64-record episodes, 8 queried + 8 outside + 8 text nulls; artifact = tensor average of steps 150/200/250/300; measured 0.24–0.25 h each |
| `epc_reader_s{0,1,2}` | same base + reader trained by error predictive coding, seed s | `assets/runs/additional_work/PC-reader/train-epc-s{s}/theta_avg150-300.npz` | identical episodes and initial parameters within seed; base-dependent answer/preservation gradient replaced by `EPCTrainer`/`EPCWriteGradients` (8 zero-initialised settling steps, error rate 0.1, corrected SD-24 energy); retrieval and reader VJP exact autodiff; 23.4–24.6 h each |

**Verified differences between PC-CAP and BP-CAP (handoff §1 demand):** architecture, parameter count (3,348,228 both), interface, initial parameters (within seed), episode sequence, acquisition rule (adjoint), evaluation population and scoring code are identical. They differ in (a) the gradient estimator for the base-dependent losses during training (settled ePC CE vs feedforward CE; ePC recomputes the teacher in float32, BP uses a cached float16 teacher), (b) resulting weights, and (c) training cost (96–102×). Finite settling changes gradient magnitude as well as direction (PC-reader.md). There is **no inference-time iteration** in either cap: both evaluate with the same feedforward read path. "Number of inference iterations" is therefore N/A at evaluation; the 8 settling steps are a *training-time* quantity.

Evaluation of the six readers (frozen record, family PCR): realization 0, order 100, first 300 edits of the sealed zsRE and CounterFact streams; checkpoints 100 and 300; endpoints locality 50, near-miss 100, revision 50, unseen 100; full 245,237-position harm assay at 300. Paths: `results/additional_work/PC-reader/eval-{bp,epc}-s{0,1,2}-{zsre,counterfact}/` with `stream/checkpoint-{100,300}.json`, `stream/items.jsonl` (per-edit immediate outcome incl. generated text and gate selection), `harm/vectors.npz` [1931,127,5], and memory snapshots in `assets/runs/additional_work/PC-reader/eval-*/stream/checkpoint-{100,300}.snapshot`.

### 1.2 Other families kept distinct

| family | backbone | what it is | where |
|---|---|---|---|
| S4 `R1_learned_ff` | GPT-2 small | selected v5 reader (BP-trained, seed 2, checkpoint average) vs registered controls; 1,000 edits (300 MQuAKE); 3 realizations × 5 orders | `results/R1/stage4_sealed_cells/R1_learned_ff-*/attempt-0000/` (checkpoint-{100,300,1000}.json, full-validation-N.npz); snapshots in `assets/runs/pc_cap/R1/stage4_sealed_cells/…` |
| FV5 (PC-v1) | GPT-2 small | v5 reader fixed; acquisition credit adjoint vs 8-step error inference; r0 o100, 300 edits | `results/additional_work/PC-v1/replication-4-20260927/`; harm in `logs/additional_work/PC-v1/report-4-20260927/harm/` |
| PCV0 | **ePC 50M base** (`assets/models/epc/epc-50m/.../params.npz`, sha `ea4c561d…`), v0 live cap | credit rule SE-E vs SE-A; depth controls | `logs/additional_work/PC-v0/…` |
| S4 controls | GPT-2 small | `v0_stable`, `R1_nonlearned` (random reader), `matched_update`, `v0_live_C1/C2`, `S1_LM`, `S1_literal` | sealed cells |

None of these is relabelled. `v0_stable`, the random reader, zero-radius caps and a condition's own cap-off are **not** the frozen baseline (amendment §3).

## 2. Frozen-baseline verification (amendment §3)

| question | finding |
|---|---|
| Exact backbone used by the PCR models | GPT-2 small, params digest `c4ac3fb8…` in every `eval-*/stream/config.json` and `train-*/report.json` |
| Are the frozen model's capless outputs on the **probes** saved? | **Partly.** Generation-level: the DATA-01 screen decoded every candidate prompt cap-off (zsRE 0/10,720 and CounterFact 0/20,391 base-correct under strict alias match) — that is the base's own-prompt answer on the eligible pools, but only as a pass/fail count plus `teacher_generation` text per eligible item. Locality and near-miss endpoints store the **cap-off reference generation** for every probe in every cell (`locality.rows[*].reference`, `near_miss.rows[*].reference`). Paraphrase prompts and MQuAKE multi-hop questions have **no** saved cap-off generation. No teacher-forced target log-probabilities are saved for any probe or any model. |
| Are the frozen model's capless outputs on **ordinary text** saved? | **Yes**: every cell's `full-validation-N.npz` holds `loss_capoff` and `loss_original` (the base's loss at all 245,237 positions) next to `loss_cap`; for GPT-2-small learned-reader cells these two references coincide (base unchanged). |
| Validation against a directly loaded frozen GPT-2 | **To do in this study** (Stage 1 tests): (i) direct `gpt2_jax.forward_jit` with `load_params_numpy` vs saved `loss_capoff` on sampled windows; (ii) direct forward vs `RevisionCap` with an empty store on probe prompts; (iii) `BPBase` vs direct forward. |
| Missing frozen evaluations to run | greedy generation + teacher-forced NLL on every PCR probe family (edit prompt, paraphrases, locality, near-miss, unseen) at the 100 and 300 horizons, for zsRE, CounterFact and MQuAKE (realization 0 order 100) — cheap (≈ 2,000 prompts per dataset). |

## 3. Datasets

| dataset | version actually used | pool | per-realization stream | probe families saved per item | other |
|---|---|---|---|---|---|
| zsRE | MEND release, `mend_train` split rows (`source_split`), via `assets/data/prepared/editing/zsre_eligible.jsonl` (10,420 eligible of 10,720 screened; 0 base-correct) | 10,420 | 1,000 items (300 used by PCR) + 1,350 pool rows | prompt, 1 paraphrase, locality prompt(s) + answers (NQ-style), `alt` not used as target | no relation ids; target = first `answers[]` entry (true answer) |
| CounterFact | original CounterFact (Meng et al.) via `counterfact_eligible.jsonl` (20,091 eligible of 20,391; 0 base-correct) | 20,091 | 1,000 + 1,350 pool rows | prompt, 2 paraphrases, ~10 neighbourhood (locality) prompts with `target_true` answers, `relation_id`, `target_true`, `target_new` | counterfactual target by construction |
| MQuAKE | **MQuAKE-CF** (`assets/data/raw/mquake/MQuAKE-CF.json`, 9,218 cases, sha `fbf1ab9e…`; DEC-045). MQuAKE-CF-3k-v2 and MQuAKE-T are present but **unused** | 9,218 cases → single-hop rewrite items | 300 single-hop edit items + 650 pool rows; 80 composition cases (multi-hop questions, 85 rows) | prompt (cloze), 1 paraphrase (question form), locality prompts/answers, near-miss candidates, `relation_id`, `target_true`/`target_new` with QIDs, `source_case_id`, hop structure via composition rows (`orig.triples`, `new_triples`, `questions`, `new_answer`, aliases) | MQuAKE ends at 300 edits; composition endpoint = registered multi-hop test (any-of-questions convention to be checked in Stage 1 tests) |

Common endpoint bundles per realization (all datasets): locality 50, near-miss 100 (distinct subjects within matched relation/template families; reference = the cell's own cap-off neighbour response), revision 50, unseen 100 (prompts of un-taught pool items; measures false firing). Ordinary-text assay: 1,931 windows × 128 tokens of OpenWebText (`drift_tokens.npy`), context reset per window, 245,237 scored positions; descriptive prefix 128 windows / 16,256 positions.

Prompt template: raw prompt text, tokenised with the GPT-2 BPE; answer tokens are the answer with a leading space plus newline terminator (answers ≤ 32 tokens); greedy decoding, max 32 new tokens, stop at newline/EOS; exact match of the NFKC/casefold/whitespace-normalised generation against supplied aliases (`src/pccap/data/decode.py`, `metrics/editing.py`).

## 4. Evaluation scripts, metrics and seeds (existing)

| metric | definition (registered) | code |
|---|---|---|
| ES | immediate edit success: own prompt yields the target right after teaching (greedy, alias exact match) | `stage4_assays.CellAssays.item` |
| RET-ES / RET-GS | end-of-stream own-prompt / paraphrase retention (fractional per item over paraphrases) | same, `retention` |
| LS | DEC-053 bounded exact decoded-text equality between cap and original-base response on 50 unrelated prompts (no normalisation) | `locality` |
| near-miss | same equality on 100 matched-family neighbours vs the cell's own cap-off response | `challenges("near_miss")` |
| revision | retire-and-replace behaviour on 50 items | `challenges("revision")` |
| unseen | firing on 100 un-taught prompts | `unseen` |
| harm | Δ = loss_cap − loss_capoff per ordinary-text position; mean KL(capoff‖cap); ES95/ES99 positive part incl. zero mass; max; exceedance fractions at 0.01/0.1/1 nat; half-mass count | `scripts/r1_68f_full_validation.py`, `aw/pc_harm_readout.py`, `aw/scoring.py` |
| tails | GPD vs exponential on positive excesses at u ∈ {0.01, 0.1, 0.5, 1}; ≥ 100 excesses in ≥ 30 windows; 200 joint-window bootstrap draws; 5-fold held-out windows | `aw/tail_class.py` (HT-17) |

Seeds: training seeds 0, 1, 2 (PCR); realization 0 only; order 100 only. Registered Stage-4 uncertainty: three-realization ranges (DEC-069); nothing here changes those labels.

## 5. Environment

Python 3.12.15 in `/home/derp/cap/venv`; jax/jaxlib 0.11.1 (CUDA device 0); numpy 2.5.3; scipy 1.18.1; pandas 3.0.5; pyarrow 25.0.1; matplotlib 3.11.1 via `assets/envs/status-paper-20260911` site-packages (as the frozen reproduction guide does); NVIDIA GeForce RTX 5070, 12,227 MiB, driver 615.71.09; Linux 7.2.9-200.fc44. No pandoc on the machine; PDF via xelatex from a converter in `aw/extremes/md2tex.py`. Code revision at audit: pc_cap `d003c10`, assets `4d25500` (later commits are recorded in `manifest.json` per stage).

## 6. Discrepancies and cautions recorded

- `aw/trained_reader_eval.py` and `aw/pc_reader_train.remaining_allowance` bind the 9 Oct 17:00 EDT cutoff (`aw/pc_v0.CUTOFF`); they will refuse to run now. New evaluations therefore use a new runner in `aw/extremes/` that reuses the same `run_stream`, `construct_owner_adapter`, `InterfaceCap`, `load_theta`, `CellAdapter`, `CellAssays` and harm readout, with its own output roots and receipts (amendment §8).
- The PCR evaluator requires a matching *development evaluation profile* per dataset; MQuAKE has none (profiles exist only for zsRE/CounterFact on the development recipes). The new runner records this and treats the MQuAKE evaluation as a new supplemental result, not a registered one.
- The PC-reader report's "ES" at the saved 300-edit memory in AW-B is a re-query equal to RET-ES; the PCR evaluations themselves record true immediate ES per item in `items.jsonl`.
- Capex's post-freeze CPU measurement (`assets/support-information/measurements.md`, pc_cap `logs/entropy-tail-measurements-20261009-release/`) already covers loss/KL tail fits for all 45 MQuAKE Stage-4 cells, harm-allocation entropy, binned-loss entropy and reader-training KL traces. It is reused, not repeated.
- Local files match the receipts checked so far (recipe, payload and vector hashes); no GitHub discrepancy was tested (the lead pushes; the local record is authoritative).
