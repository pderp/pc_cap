# Response to the Stage 0 counter-review (R1-X1) — orchestrator, 2026-09-13 late evening

| id | disposition | how it lands |
| --- | --- | --- |
| X1-01 prefix identity | **adopted** | The verification rule (owner + activity + presented token) is kept for these artifacts; a same-owner same-token different-prefix fixture and a chronological last-accepted check go into the diagnostic before it is reused on new streams (noted in the script header). |
| X1-02 C1 hybrid rebuild | **adopted** | The memo now says C1's rebuild is near-complete (five site-2 slots keep stored keys); a drop-unverifiable variant is listed as a sensitivity check. |
| X1-03 exactness/NLL definitions | **adopted** | Memo footnote: teacher-forced argmax exactness ≡ greedy exact canonical sequence; `tf_nll_token_mean` is the mean of per-answer token means; free-generation exactness is the report endpoint. |
| X1-04 "storage exonerated" too strong | **adopted** | Memo §3.1 reworded: storage is adequate for most tested paraphrases when the surviving entries are supplied, on this short low-pressure stream; the .67/.49 → .94 residual is a target, not an attainable ceiling. |
| X1-05 locality population | **adopted** | Memo §2/§3.5 corrected: zero unrelated firings were measured under the live policy only; other-owner range 22–28 %; in-stream LS/firing evidence belongs to the v0-stable and matched-update conditions. |
| X1-06 non-uniform NLL | **adopted** | "NLL moves the same way" restricted to C1; C2's paraphrase NLL worsens (8.12 → 8.33) while exactness improves. |
| X1-07 capacity units | **adopted** | 2,048 slots per bank (6,144 total); C1 rebuild = 1,080 keys from 367 unique prefix passes, C2 374 from 365. |
| X1-08 DEC-035 qualification | **adopted** | DEC-035 rationale now names .67/.49 as the post-hoc shadow assay and .44 as the in-stream comparator. |
| "What would change the diagnosis" 1–5 | **adopted as the Stage 1–2 checklist** | Items 3 (matched development comparison incl. support-answer swaps) and 4 (pressure controls) are folded into R1-25 and the next stream evaluation; item 2 (four-policy rerun on the full near-miss/unrelated set with traces) is a bounded GPU diagnostic queued after the current pilots. |
