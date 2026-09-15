# R1-X10 — MQuAKE, IDF and composition counter-review

Codex, 2026-09-15. **Review complete; repairs requested, not applied.** CPU only, no base execution, no sealed
payloads. The [recount](r1_round12/mquake_review_evidence.json) binds the inspected code, 27 stored stream summaries,
composition rows and teacher/prepared inputs. [Population evidence](r1_round12/population_options.json) independently
checks the cumulative supplement and archived R1-X9 audit. Reproduce with
`scripts/r1_x10_mquake_audit.py --output <new-repository-file>`; all outputs refuse overwrite.

The important numerical development results are supported, including composition's 0/897 base exact count.
The main outstanding issues are population-policy claims, unchecked development overrides, incomplete firing
traces and causal interpretations stronger than the evidence. See the concrete
[edit requests](../docs/tasks/R1-X10-edit-requests.md). No production file, old result or manifest was changed.

## Findings requiring action

### X10-01 — high: split remainder is not a fresh confirmatory population

Targets: [r1_d6_mquake_split.py](../scripts/r1_d6_mquake_split.py:1), especially the unrelated selection and
`remaining_for_confirmatory` at lines 61–68; DEC-046 and the older pool metadata.

The producer excludes selected primary IDs/subjects from its remainder but then samples first locality prompts
from that remainder for development unrelated queries. Its training and development locality rows also introduce
subjects outside the primary slices. “Rest untouched” and “remaining for confirmatory” therefore overstate the
remainder's freshness and confuse source items with independent subjects.

The effective cumulative population is **2,171 items / 2,100 MQ subjects**, with 1,200 historical primary,
2,106 locality and 990 unrelated-query subjects, union 3,405. New self-contained train500/dev100 v3 slices contain
their new query roles, but do not erase historical exposure. The 4,818 prospective ceiling is not obtained by
waiving only true-query exposure; with historical primary exclusions that ceiling is **4,218**.
R1-D7 supplies exact arithmetic and the executed-only review classes.

Required change: label historical counts as primary-only item remainders; point current readers to the cumulative
supplement; distinguish reservations, matched execution and certified release. Keep old records as historical.
Any new policy needs a lead decision and versioned register. Do not rerun the old split to create a “fresh” draw.

### X10-02 — high before reuse: development manifest override bypasses admission checks

Target: [r1_13_stream_eval.py](../scripts/r1_13_stream_eval.py:93).

A CPU AST probe executes only the existing override branch against an in-memory synthetic manifest. It accepts
a manifest declaring `mode=confirm`, `dataset=mquake` while CLI dataset is zsRE, and assigns zsRE to its items.
Requesting 100 items from one returns one silently; `n=-1` on three rows returns two. Arbitrary stored token arrays
are accepted without round-trip or digest validation. The summary records a path string, not the selected
manifest content hash. Replacing that file later loses the exact query/LS population identity.

This is a development CLI, not proof that the final cell driver's separate admission checks are broken.
The test did not read a real confirm payload. Nevertheless, a typo can silently change dataset, sample size and
conditioning, and the unrestricted path could accidentally select an unintended population.

Requested repair: a pure preflight loader before base/lease/output creation, requiring development mode,
dataset agreement, positive count within available size, unique IDs/facts/subjects, valid ordered tokens/digests,
source bindings and enough explicit unrelated queries. Pin manifest bytes, selected IDs and query inventory.
Preserve the declared sampling rule. A versioned wrapper/helper under scripts is possible, but the existing CLI
call site and receipt must be changed with permission. Do not retrofit invented hashes into historical results.

### X10-03 — high for interpretation: null mass does not identify actual cap firing

Targets: [endpoint trace](../src/pccap/revision_v1/endpoints.py:150) and
[composition note](../docs/R1_stage2_notes.md:708).

The rows contain candidate record IDs, null mass, best score and prompt length. They do not record
`Selection.hard_null`, final selected weights/index, or the post-selection rare-token veto.
The **369/897** count for null mass below .5 is reproducible. Calling it the number of actual cap fires is not
supported by these traces: the rare gate executes after that threshold. Nor do the rows alone prove that all
369 questions explicitly name the edited subject or that every accepted selection changed an answer.

Requested repair: label the historical count as “null mass < .5, actual post-gate firing unavailable.”
Add final hard-null/gate result and selected record/weight to future traces, using the already cached prompt-only
selection. Tests must include low-null selection vetoed by the rare gate, and verify no second selection pass
or answer leakage. An owner-approved src change requires refreshing affected code identities after active jobs.

### X10-04 — medium: floor arithmetic is sound; floor interpretation overreaches

Targets: R1-60 note, composition summary and [runner](../scripts/r1_60_composition_run.py).

Recount agrees with the stored summary:

| Quantity | Observed value |
| --- | ---: |
| Planned / scored / unavailable cases | 300 / 299 / 1 |
| Planned / scored questions | 900 / 897 |
| All-three success | 1/299 scored |
| Post-edit question exact | 8/897 |
| Cap-off exact against pre-edit / post-edit aliases | 0/897 / 0/897 |
| Pre-edit alias reappearance | 0 |
| Reference / cap outputs hitting decode maximum | 7 / 7 |
| Empty-state restoration | All 300 rows report restored |
| Selected edited-dependency counts | 266 one-edit, 34 two-edit, zero three-edit |
| Wall time | 195.047649 seconds |

The unavailable case is `mquake:case:2011`, `pre_and_post_aliases_overlap`. The full-inventory rates are **null**,
as implemented; do not silently impute it as failure or report 1/299 as if all 300 were scored.
Nontermination is a scored non-exact answer, not an additional missing row. The number of edited dependencies
does not equal the number of hops in a source path.

This is a source-order development subset attached to an exposed training pool, with each case taught on an
isolated empty clone, not a final 1,000-record stream. Pre/post cap-off exact are two comparisons of the same
cap-off generation against different alias sets, not two independent baseline trials.

Zero exact base answers establishes a floor under this base/prompt/decoding convention. It does not establish
“no headroom,” impossibility of composition, or irrelevance to the reader: cap-on produces eight exact questions
and one all-three success. The upstream task includes different prompting/evaluation conventions; its README
describes an any-of-three editing success rule, whereas this project uses all-three. Do not claim comparability
without aligning protocols. Composition should remain descriptive, with prompt suitability and single-hop
controls considered before a stronger capability conclusion.

The runner computes input hashes after execution rather than verifying prepared source identities before use.
It also excludes source-unavailable attached cases before its chosen inventory, while reporting their count.
In this run that count is zero, so it does not explain the one alias-overlap unavailability. Future use must
declare whether structural failures remain in the planned inventory and bind ordered selected IDs before
execution; no outcome filtering or replacement should be introduced.

### X10-05 — medium: teacher pool supports bounded new-answer exclusion, not complete truth certification

Target: [r1_d5_mquake_teacher.py](../scripts/r1_d5_mquake_teacher.py).

Positive checks: it verifies prepared-item bytes, tokenizes prompt/answer pairs and compares ordered token arrays,
requires paraphrases and locality, normalizes new-answer aliases, refuses an existing output and preserves
source support fields. All 6,043 output rows match the inspected prepared prompt/answer/token/digest/subject/fact/
relation fields. The stored counts report zero teacher-correct new answers, zero token failures and 6,043 eligible.

However **2,807/6,043** teacher outputs stop at the token limit; 3,219 stop at newline and 17 at EOS.
The script compares bounded text to the new-answer aliases regardless of termination. This can be consistent
with a declared bounded base-wrong-new-answer rule; it is not evidence that the base knows the true old answer,
or that all answers were complete. No old-answer correctness test is performed. Source locality answers also
are not independently teacher-certified.

The receipt binds source items/manifest and elapsed seconds but lacks explicit producer-code, base checkpoint,
tokenizer, decoder/max-token identities and a full ledger. It also relies on zip length agreement without checking
the number of returned generations. Historical base provenance can only be recovered from genuine contemporaneous
records; a later code hash does not prove which producer ran.

Request: version future receipts with those identities, exact eligibility/truncation rule, input/output cardinality,
reasons and charged costs. Retain current bounded results; if a stricter rule is chosen, measure its changed yield
before population allocation. A blanket rerun is not required by this review alone.

### X10-06 — qualified result: IDF paths share a definition, not a fixed population

Targets: `reader.idf_weights`, `train.lex_matrix`, `train_fast.pack_episode`, `learner._lex_weights`.

The shared formula is log((N+1)/(df+1))/log(N+1), over distinct non-stop tokens in each non-None support prompt.
Training computes it over episode supports; fast training calls the same `lex_matrix`. Deployment computes it
over all active records' support prompts, not the top-k retrieved candidates. Cache keys include store object
identity and lexical mutation version; the CPU test checks reuse, mutation and replacement/restore identity.

No different-formula bug was found. Given the same support population, training lexical features and deployed
weights agree. But 64-record mixed training episodes and 100–1,000-record deployed stores do not have the same
size or relation-frequency mixture. A singleton's normalized weight is about .834 at N=64 and .900 at N=1,000;
tokens absent from memory use weight 1. All-memory tokens have weight zero, and a one-record memory gives every
present token zero weight. Those are properties of the implemented rule, not evidence of a cache failure.

Thus IDF is not an invariant substitute for the rare-token gate; its feature distribution changes with memory.
This is worth measuring in matched-memory diagnostics if revisited, not a reason to enable it now.

The 27 stream summaries reproduce the notes' GS values. ES and RET-ES differ in some IDF runs: MQ seed0 is
.85/.86; CF seed0 .96/.97; zsRE seeds all have immediate ES .99 and retained ES 1. The v4 plain MQ seed0 already
has ES/RET-ES .92, so “introduces own-prompt rejections” must be qualified for MQ. The three IDF MQ GS differences
from matching plain v4 seed numbers are −.17/+.06/+.24; same numeric seed does not alone establish a paired
causal experiment. IDF's zsRE outside 12% versus the two-pool v3 10–11% changes training identity as well.

### X10-07 — medium: primary v4 metadata combines multiple reference populations

Target: [primary_condition_v4.json](../manifests/revision_v1/primary_condition_v4.json).

The v4 weights and GS triplets match the intended three-pool MQ-v2 readers. The own-prompt seed0 .92 result is
correct, but both immediate ES and RET-ES should be explicit. The v4 risk range is .56–.79; .47–.82 pools
three earlier 500-MQ readers with the three 1,000-MQ readers. “Lexical feature alone” overstates diagnostic
evidence. The MQ +.005 drift is marked pool-v1 in one field, but adjacent outside/risk entries can still be
mistaken for v4 measurements. CounterFact +.012 and zsRE 10–11% are inherited older-reference assays.

The control list's pending teacher-only variant language predates DEC-047's two specific continuation controls.
A new reference version should bind per-result file, reader hash, dataset/split and metric convention rather
than merge older assays into a single current-condition string. Active self-contained tri3 training is not
identical to v4 even if most settings agree.

Do not edit a bound primary manifest in place to pretend it describes newly trained weights.
Use a new version, keep its training history, refresh matrix/profile/freeze candidate and preserve v3 fallback.
The round-12 matrix deliberately binds historical v4 and flags later substitution as unresolved.

## Disposition and verification

The CPU suite passes **507 tests, 8 skipped**, including 23 new round-12 invariants; four new Python files pass
Ruff. Counts and stored evidence were checked without teacher or real-base execution. The GPU owner's new
stream results and `results/R1/stream_eval.md` updates are its work, outside this review's selected evidence.

Next lead/owner steps: choose population scope; approve/apply requested loader/trace repairs in an appropriate
code-identity window; qualify historical reporting; bind final self-contained reader and measured profiles;
then perform final admission. These review requests do not authorize those mutations, final draws or GPU jobs.
