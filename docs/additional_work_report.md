# Supplemental programme: predictive coding, bounded correction and rare harm

**Completed results through October 4, 2026; assembled October 5 (FIN-1).** This is the consolidated entry point after the Stage-4 halt, with the earlier κ pilot retained as context. Lettered citations link the exact reports; the accompanying registry records their SHA-256 hashes. Headline tables are copied verbatim, without rescoring, new fits or reclassification.

## Main finding and scope

The programme supports selective correction with measurable trade-offs. Corrected predictive-coding acquisition changes some outcomes but establishes no broad advantage over adjoint credit. Training the reader with the installed ePC procedure is far more expensive and loses CounterFact paraphrase retention. A query-time mixture supplies a proven one-nat ceiling at an identical prefix; it reduces severe observed harm without resolving every fidelity or retention limitation. Upper-layer restriction is not a demonstrated improvement. The additional subject realization reinforces learned-versus-random paraphrase retention, while the stable-v0 extension remains incomplete. [A] [D] [F] [G] [H] [I]

For a reader new to the project: a **cap** is a small correction/memory mechanism attached to a frozen language model. Acquisition writes requested facts into memory; readout decides when to apply them. **ES** is immediate edit success, **RET-ES** retention on original edit prompts, **RET-GS** retention on paraphrases, and **LS** locality preservation. Higher task scores are usually desirable. ΔNLL is cap loss minus its own cap-off loss at the same text prefix; positive values mean harm, measured in nats. A small average does not preclude rare large changes. ES99+ averages the worst 1% of positive-part losses, including zero mass in its denominator. [P] [L]

The main Stage-4 report [P] covers 270 completed cells and remains separate. Passing data-integrity checks does not imply passing its mean-KL ≤.001 benchmark: all 45 main learned-reader cells fail that benchmark. The supplements change different parts of the system and use different populations; their cells must not be pooled as independent confirmations. Most are post hoc studies on exposed subjects. Option R's new r3 subject draw and the reader's three training seeds provide different kinds of replication. [P] [G] [H]


## PC-v0: does corrected error settling improve acquisition?

**Design and exposure.** DEC-074/074b authorized corrected SE-E versus adjoint SE-A with fresh memories on the original **ePC 50M frozen base and v0 C1 live cap**, not the GPT-2-small main-study model. Sixty cells cross two datasets, three previously exposed S5 subject realizations, five orders and two arms. zsRE reaches 1,000 edits; CounterFact reaches 300. Eight error iterations at rate .1 use the corrected quadratic error prior. Credit computation still uses autodifferentiation; this is not a demonstration of local, backpropagation-free learning. [A] [N]

**Reading and limits.** zsRE own-prompt retention improves by .0203333, while paraphrase retention changes by −.0028 with mixed realization signs. CounterFact saturates own-prompt retention with zero paraphrase retention in both arms. The harm readout uses only 32 windows / 4,064 positions, and cannot be directly pooled with the full 245,237-position assay below. Positive-loss expected shortfall and the difference between two arms' shortfalls are distinct from the shortfall of paired loss differences. [A]

Copied unchanged from [A] (line 48):

| Dataset | metric | r0, r1, r2 | mean | min | max |
| --- | --- | --- | --- | --- | --- |
| zsre | ES | [0.0010000000000000009, 0.0006000000000000005, 0.00020000000000000017] | 0.0006 | 0.0002 | 0.001 |
| zsre | RET-ES | [0.02200000000000002, 0.019799999999999974, 0.019200000000000016] | 0.0203333 | 0.0192 | 0.022 |
| zsre | RET-GS | [-0.005400000000000002, 0.002200000000000002, -0.00520000000000001] | -0.0028 | -0.0054 | 0.0022 |
| zsre | LS | [0.03799999999999999, -0.006000000000000005, 0.028000000000000004] | 0.02 | -0.006 | 0.038 |
| zsre | bounded_es_immediate | [0.0010000000000000009, 0.0006000000000000005, 0.00020000000000000017] | 0.0006 | 0.0002 | 0.001 |
| zsre | bounded_ret_es_end | [0.02200000000000002, 0.019799999999999974, 0.019200000000000016] | 0.0203333 | 0.0192 | 0.022 |
| zsre | bounded_ret_gs_end | [-0.005400000000000002, 0.002200000000000002, -0.00520000000000001] | -0.0028 | -0.0054 | 0.0022 |
| zsre | bounded_ls_end | [0.03799999999999999, -0.006000000000000005, 0.028000000000000004] | 0.02 | -0.006 | 0.038 |
| counterfact | ES | [0.0, 0.0, 0.0] | 0 | 0 | 0 |
| counterfact | RET-ES | [0.0, 0.0, 0.0] | 0 | 0 | 0 |
| counterfact | RET-GS | [0.0, 0.0, 0.0] | 0 | 0 | 0 |
| counterfact | LS | [0.0, 0.0, 0.0] | 0 | 0 | 0 |
| counterfact | bounded_es_immediate | [0.0, 0.0, 0.0] | 0 | 0 | 0 |
| counterfact | bounded_ret_es_end | [0.0, 0.0, 0.0] | 0 | 0 | 0 |
| counterfact | bounded_ret_gs_end | [0.0, 0.0, 0.0] | 0 | 0 | 0 |
| counterfact | bounded_ls_end | [0.0, 0.0, 0.0] | 0 | 0 | 0 |


Copied unchanged from [A] (line 418):

| Dataset | Arm | Cells | Mean KL | Mean ΔNLL | Mean ES99+ | Mean of cell maxima | Largest single maximum | P(>0.01) | P(>0.1) | P(>1) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 15 | 0.00164535 | 0.00159508 | 0.172534 | 3.66962 | 10.4233 | 0.000885827 | 0.000836614 | 0.000524934 |
| zsre | SE-E | 15 | 0.00193136 | 0.00175622 | 0.189069 | 3.48573 | 9.89738 | 0.00100066 | 0.000951444 | 0.000672572 |
| counterfact | SE-A | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact | SE-E | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |


**Measured cost:** 51,429.816123 receipt-backed process seconds (14.286060 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## PC-v0 control 1: settling depth

**Design and exposure.** DEC-075 adds one- and 32-step settling to the eight-step reference, using order 100 only, the same three exposed realizations and both datasets: twelve cells per depth. The eight-step rows reuse the default study and are charged there. [B] [N]

**Reading and limits.** One-step normalized credit matches adjoint algebraically; tiny saved harm-vector differences are floating-point effects. More settling raises zsRE own-prompt retention but does not consistently improve paraphrase retention or harm, and costs more. CounterFact's saturation limits discrimination. Three realizations and one order do not establish general PC superiority. [B]

Copied unchanged from [B] (line 9):

| Dataset | Depth | Arm | ES | RET-ES | RET-GS | LS | Mean KL | Mean ΔNLL | ES99+ | Mean cell max | Largest maximum | Learning s/cell | Process s/cell |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 1 | SE-A | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184295 | 0.00145132 | 0.155812 | 3.6504 | 5.46859 | 275.934 | 1008.01 |
| zsre | 1 | SE-E | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184297 | 0.00145136 | 0.155816 | 3.6504 | 5.46857 | 341.182 | 1092.51 |
| counterfact | 1 | SE-A | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 45.4616 | 436.964 |
| counterfact | 1 | SE-E | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 59.3532 | 455.701 |
| zsre | 8 | SE-A | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184295 | 0.00145132 | 0.155812 | 3.6504 | 5.46859 | 280.837 | 1024.99 |
| zsre | 8 | SE-E | 0.999 | 0.534 | 0.131 | 0.976667 | 0.0021476 | 0.00157227 | 0.166889 | 2.39772 | 3.24707 | 614.015 | 1342.27 |
| counterfact | 8 | SE-A | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 45.3522 | 435.266 |
| counterfact | 8 | SE-E | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 107.861 | 505.132 |
| zsre | 32 | SE-A | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184295 | 0.00145132 | 0.155812 | 3.6504 | 5.46859 | 273.309 | 988.69 |
| zsre | 32 | SE-E | 0.999 | 0.565 | 0.122 | 0.996667 | 0.00257776 | 0.0022107 | 0.23644 | 4.36855 | 8.02868 | 1524.85 | 2238.27 |
| counterfact | 32 | SE-A | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 45.6985 | 438.064 |
| counterfact | 32 | SE-E | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 269.302 | 665.56 |


**Measured cost:** 23,531.539732 receipt-backed process seconds (6.536539 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## PC-v0 control 2: random credit direction

**Design and exposure.** DEC-075/079 replace the true credit's direction with a random direction of equal norm, paying for the true credit first. Of six planned pairs, only the first exposed zsRE r0/order-100 pair ran. Adjoint completed 1,000 items; random credit stopped under its unchanged resource allowance at 993. Ten cells were never started. [B] [N]

**Reading and limits.** Three random-arm immediate answers succeeded. The table's immediate-ES denominators differ; on the common first 993 items, adjoint is .997986 versus .003021 for random credit. Missing final retention and separate full-vector control harm remain missing. This supports informative credit in this implementation, not a general impossibility of random search. The native report corrects DEC-079's historical unstarted-cell count. [B]

Copied unchanged from [B] (line 117):

| Arm | Status | Items | Immediate ES | Process seconds | Total forwards | Total reverses |
| --- | --- | --- | --- | --- | --- | --- |
| SE-A | complete | 1000 | 0.998 | 989.738 | 139630 | 11334 |
| SE-R | resource_stop | 993 | 0.00302115 | 3727.43 | 641262 | 340155 |


**Measured cost:** 5,230.062203 receipt-backed process seconds (1.452795 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## PC-v0 control 3: adjoint offered the PC acquisition budget

**Design and exposure.** DEC-075 and the lead's clarification fund additional acquisition updates for adjoint. Twelve cells / six pairs use the same exposed populations and order 100. The first table is SE-AM minus ordinary SE-A. [B] [C] [N]

**Reading and limits.** The control uses only about 53–58% of the offered operations because threshold stopping and rollback remain active. It does not recover the eight-step own-prompt gain, but it is **not an equal-realized-compute comparison**. Operations are not FLOPs; differences in prefix traversal and stopping leave direction versus effective compute unresolved. Separate full-vector control harm curves were not supplied. [B] [C]

Copied unchanged from [C] (line 7):

| Dataset | Realization | ES | RET-ES | RET-GS | LS | bounded_es_immediate | bounded_ret_es_end | bounded_ret_gs_end | bounded_ls_end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | -0.019 | -0.012 | 0.01 | 0 | -0.019 | -0.012 | 0.01 | 0 |
| zsre | 1 | -0.013 | -0.002 | 0.018 | 0.015 | -0.013 | -0.002 | 0.018 | 0.015 |
| zsre | 2 | -0.013 | -0.008 | 0.006 | 0.035 | -0.013 | -0.008 | 0.006 | 0.035 |
| counterfact | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |


Copied unchanged from [C] (line 33):

| Dataset | Realization | Offered ops | Used ops | Threshold stops | Incomplete round rollbacks |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | 391311 | 225484 | 945 | 55 |
| zsre | 1 | 380888 | 219015 | 953 | 43 |
| zsre | 2 | 388261 | 225589 | 962 | 35 |
| counterfact | 0 | 61344 | 32996 | 300 | 0 |
| counterfact | 1 | 62026 | 33456 | 300 | 0 |
| counterfact | 2 | 61096 | 32628 | 300 | 0 |


**Measured cost:** 9,023.390972 receipt-backed process seconds (2.506497 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## Fixed-v5 reader: change acquisition credit only

**Design and exposure.** DEC-074/074b hold the selected BP-trained v5 reader and frozen GPT-2-small base fixed, comparing SE-A and corrected SE-E acquisition into fresh memories. Four cells use both datasets, exposed r0/order 100, through 300 edits. The efficacy table is checkpoint 300. Full ordinary-text harm uses 1,931 windows / 245,237 positions. [D] [N]

**Reading and limits.** Paraphrase differences are zero on zsRE and −.003333 on CounterFact; ES99+ falls on zsRE and rises on CounterFact. This is one exposed realization, not an equivalence test. The original harm invocation finished its numerical readouts but failed while formatting its final table; the failed receipt remains failed, and saved vectors were independently verified. [D]

Copied unchanged from [D] (line 16):

| Dataset | Arm | ES | RET-ES | RET-GS | LS | Near miss | Revision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| zsre | SE-E | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| counterfact | SE-A | 1 | 1 | 0.806667 | 1 | 1 | 1 |
| counterfact | SE-E | 1 | 1 | 0.803333 | 1 | 1 | 1 |


Copied unchanged from [D] (line 38):

| Dataset | Arm | Cells | Mean KL | Mean ΔNLL | Mean ES99+ | Mean of cell maxima | Largest single maximum | P(>0.01) | P(>0.1) | P(>1) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 1 | 0.00186062 | 0.00181293 | 0.195585 | 9.26227 | 9.26227 | 0.00117845 | 0.00112952 | 0.000619809 |
| zsre | SE-E | 1 | 0.00170361 | 0.00167283 | 0.181614 | 12.27 | 12.27 | 0.00118253 | 0.00112136 | 0.000591265 |
| counterfact | SE-A | 1 | 0.00417566 | 0.0043814 | 0.458686 | 11.7442 | 11.7442 | 0.00281768 | 0.00267904 | 0.00140272 |
| counterfact | SE-E | 1 | 0.00430833 | 0.00450374 | 0.469916 | 12.2254 | 12.2254 | 0.00284623 | 0.0026872 | 0.00145981 |


**Measured cost:** 6,921.982280 receipt-backed process seconds (1.922773 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## Fixed-v5 settings: deeper settling and two error rates

**Design and exposure.** DEC-077 adds 32 iterations at rate .1, and rates .05/.2 at eight iterations. Each setting has its own development profile, four exposed r0/order-100 cells through 300 edits and full-vector harm. The table is copied from the completed Round-63 reproduction; all setting-specific harm statistics and costs remain in its companion report [R]. [E] [N]

**Reading and limits.** None supplies an independent subject replication or demonstrates a broad advantage over adjoint. The default/settings use repeated subjects and cannot be counted as new independent realizations. Three failed initial harm launches have logs but no separate preserved duration receipt; the cost total explicitly leaves that gap open. [E] [R]

Copied unchanged from [E] (line 5):

| Setting | Dataset | Arm | ES | RET-ES | RET-GS | LS | Near miss | Revision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| k32 | zsre | SE-A | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| k32 | zsre | SE-E | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| k32 | counterfact | SE-A | 1 | 1 | 0.806667 | 1 | 1 | 1 |
| k32 | counterfact | SE-E | 1 | 1 | 0.8 | 1 | 1 | 1 |
| lr0.05 | zsre | SE-A | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| lr0.05 | zsre | SE-E | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| lr0.05 | counterfact | SE-A | 1 | 1 | 0.806667 | 1 | 1 | 1 |
| lr0.05 | counterfact | SE-E | 1 | 1 | 0.803333 | 1 | 1 | 1 |
| lr0.2 | zsre | SE-A | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| lr0.2 | zsre | SE-E | 1 | 1 | 0.983333 | 1 | 0.76 | 1 |
| lr0.2 | counterfact | SE-A | 1 | 1 | 0.806667 | 1 | 1 | 1 |
| lr0.2 | counterfact | SE-E | 1 | 1 | 0.8 | 1 | 1 | 1 |


**Measured cost:** 21,189.820529 receipt-backed process seconds (5.886061 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## AW-B: a bounded query-time correction

**Design and exposure.** DEC-073/076/076a prescribe development calibration on the actual full-endpoint saved-memory populations, eligibility on both datasets, then maximize the smaller maximum-harm reduction (ES99 reduction breaks ties). The selected mixture uses ρ=exp(−1). Evaluation uses ten already exposed r0 memories: two datasets × five orders at 300 edits. No eligible shrinkage or stricter-gate comparator was selected. [F] [N]

**Reading and limits.** All ten evaluation coordinates pass the registered comparison rule. Mixing p_mix=ρ p_base+(1−ρ)p_cap proves ΔNLL≤−lnρ=1 nat **for a token at the identical prefix**. Severity drops substantially, frequency changes little, and CounterFact loses some paraphrase retention. This is not a sequence-level or KL bound, nor a recommended cap configuration (DEC-078). It is a known ceiling on the observable, not a demonstrated change in distribution class (DEC-081a). Group frequency/severity results are also copied in HT-17 below. [F] [L] [N]

Copied unchanged from [F] (line 114):

| Memory | Setting | ΔES | ΔRET-ES | ΔRET-GS | ΔLS | Δnear_miss | Δrevision | Δmean KL | Δmean NLL | ΔES99+ | Δmaximum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre-o103 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o103 | capoff | -1 | -1 | -0.983333 | 0 | 0.17 | -1 | -0.00146107 | -0.00156859 | -0.162834 | -9.26227 |
| zsre-o103 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00100858 | -0.00108844 | -0.110632 | -8.26243 |
| zsre-o100 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o100 | capoff | -1 | -1 | -0.983333 | 0 | 0.24 | -1 | -0.00186062 | -0.00181293 | -0.195585 | -9.26227 |
| zsre-o100 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00127724 | -0.00126888 | -0.130243 | -8.26243 |
| counterfact-o102 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o102 | capoff | -1 | -1 | -0.748333 | 0 | 0 | -1 | -0.00690961 | -0.0068986 | -0.71135 | -15.3818 |
| counterfact-o102 | mixture:0.367879 | 0 | 0 | -0.00666667 | 0 | 0 | 0 | -0.00496172 | -0.00494554 | -0.499595 | -14.3818 |
| counterfact-o103 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o103 | capoff | -0.996667 | -0.996667 | -0.758333 | 0 | 0 | -1 | -0.00532 | -0.00547311 | -0.564284 | -11.7442 |
| counterfact-o103 | mixture:0.367879 | 0 | 0 | -0.01 | 0 | 0 | 0 | -0.00387291 | -0.0039883 | -0.403384 | -10.7443 |
| zsre-o101 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o101 | capoff | -1 | -1 | -0.993333 | 0 | 0.2 | -1 | -0.00176972 | -0.00186703 | -0.195796 | -12.2931 |
| zsre-o101 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00118951 | -0.00126573 | -0.129092 | -11.2931 |
| zsre-o102 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o102 | capoff | -1 | -1 | -0.983333 | 0 | 0.23 | -1 | -0.00186937 | -0.00186419 | -0.194865 | -8.30384 |
| zsre-o102 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00128681 | -0.00128888 | -0.131336 | -7.30426 |
| counterfact-o104 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o104 | capoff | -1 | -1 | -0.795 | 0.02 | 0 | -1 | -0.00641211 | -0.00662269 | -0.690296 | -11.7442 |
| counterfact-o104 | mixture:0.367879 | 0 | 0 | -0.0116667 | 0 | 0 | 0 | -0.004475 | -0.00466551 | -0.473634 | -10.7443 |
| counterfact-o101 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o101 | capoff | -1 | -1 | -0.726667 | 0 | 0 | -1 | -0.00491337 | -0.0050381 | -0.51939 | -15.3818 |
| counterfact-o101 | mixture:0.367879 | 0 | 0 | -0.01 | 0 | 0 | 0 | -0.00357403 | -0.00365193 | -0.369578 | -14.3818 |
| zsre-o104 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o104 | capoff | -1 | -1 | -0.976667 | 0 | 0.22 | -1 | -0.00202264 | -0.00196767 | -0.212105 | -12.2931 |
| zsre-o104 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00136945 | -0.00135674 | -0.139705 | -11.2931 |
| counterfact-o100 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o100 | capoff | -1 | -1 | -0.806667 | 0 | 0 | -1 | -0.00417566 | -0.0043814 | -0.458686 | -11.7442 |
| counterfact-o100 | mixture:0.367879 | 0 | 0 | -0.0116667 | 0 | 0 | 0 | -0.00291063 | -0.00305252 | -0.311073 | -10.7443 |


Copied unchanged from [F] (line 151):

| Setting | Every coordinate passes |
| --- | --- |
| capoff | False |
| mixture:0.367879 | True |
| v5 | False |


**Measured cost:** 40,551.089019 receipt-backed process seconds (11.264191 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## PC-trained reader: three paired training seeds

**Design and exposure.** DEC-077 trains the v5 reader recipe for 300 steps with corrected ePC versus BP, three paired seeds each. All six trainings and twelve evaluations are complete. Evaluation remains the same exposed r0/order-100 subjects, both datasets at 300 edits, with adjoint acquisition for both reader families. Seeds are training replications, not fresh subject draws. [G] [N]

**Reading and limits.** CounterFact ePC loses paraphrase retention in all three pairs; zsRE differences are mixed. CounterFact harm/firing signs reverse across seeds; a universal safer-reader claim is unsupported. The training-time ratios are about 96–102× BP under the installed JAX implementation. This compares the implemented training procedures, not all possible PC methods. Six BP full-read evaluation controls are later reused by AW-L and charged only here. [G]

Copied unchanged from [G] (line 10):

| Dataset | Seed | BP RET-ES | ePC RET-ES | RET-GS difference (percentage points) | BP fired | ePC fired |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 1 | 1 | -2.666667 | 18 | 0 |
| counterfact | 0 | 1 | 1 | -24.16667 | 256 | 185 |
| zsre | 1 | 1 | 1 | -2 | 13 | 6 |
| counterfact | 1 | 0.99 | 1 | -2.166667 | 660 | 720 |
| zsre | 2 | 1 | 1 | 0.3333333 | 21 | 0 |
| counterfact | 2 | 1 | 1 | -17.5 | 149 | 353 |


Copied unchanged from [G] (line 36):

| Paired seed | Measured ePC/BP training time |
| --- | --- |
| 0 | 102.1063 |
| 1 | 95.75201 |
| 2 | 96.73392 |


**Measured cost:** 286,632.424427 receipt-backed process seconds (79.620118 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## Option R: a fourth subject realization

**Design and exposure.** DEC-073 reserves fresh subjects; DEC-077 launches realization 3, both datasets, five orders, 1,000 edits. DEC-080 defers the v0 class after its first cell hits a ceiling: twenty learned/random cells complete, one v0 cell incomplete and nine v0 cells unrun. Realization 3 was untouched at allocation; the four-realization sensitivity combines it with the already observed r0–2. [H] [N]

**Reading and limits.** Learned-minus-random paraphrase retention stays positive in the four-realization display. Five orders are first averaged within each realization; they are not twenty independent replicates. The t(3) intervals are unadjusted small-cluster sensitivity displays, not reissued registered classifier labels or a new familywise coverage claim. Missing v0 results remain unavailable. Its scalar drift path and unchanged ceiling explain the stopped cell; no post-outcome repair was substituted. [H]

Copied unchanged from [H] (line 135):

| Dataset | Edits | Metric | Paired orders per r0/r1/r2/r3 | Estimate | 95% t(3) display | Status |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 100 | ES | 5/5/5/5 | 0 | [0.0, 0.0] | four-realization sensitivity |
| zsre | 100 | RET-ES | 5/5/5/5 | 0 | [0.0, 0.0] | four-realization sensitivity |
| zsre | 100 | RET-GS | 5/5/5/5 | 0.3335 | [0.2973660350687092, 0.36963396493129075] | four-realization sensitivity |
| zsre | 100 | LS | 5/5/5/5 | 0 | [0.0, 0.0] | four-realization sensitivity |
| zsre | 300 | ES | 5/5/5/5 | -0.0001666667 | [-0.0006970743842140367, 0.0003637410508807067] | four-realization sensitivity |
| zsre | 300 | RET-ES | 5/5/5/5 | -0.0003333333 | [-0.00094579541034579, 0.00027912874367913023] | four-realization sensitivity |
| zsre | 300 | RET-GS | 5/5/5/5 | 0.3948333 | [0.3668286764790931, 0.4228379901875735] | four-realization sensitivity |
| zsre | 300 | LS | 5/5/5/5 | 0.001 | [-0.0021824463052842647, 0.004182446305284266] | four-realization sensitivity |
| zsre | 1000 | ES | 5/5/5/5 | -0.0047 | [-0.0077023138397835055, -0.0016976861602165032] | four-realization sensitivity |
| zsre | 1000 | RET-ES | 5/5/5/5 | -0.016 | [-0.024008980901345123, -0.007991019098654907] | four-realization sensitivity |
| zsre | 1000 | RET-GS | 5/5/5/5 | 0.44075 | [0.4156115278094418, 0.4658884721905581] | four-realization sensitivity |
| zsre | 1000 | LS | 5/5/5/5 | 0.005 | [-0.010912231526421325, 0.020912231526421333] | four-realization sensitivity |
| counterfact | 100 | ES | 5/5/5/5 | 0 | [0.0, 0.0] | four-realization sensitivity |
| counterfact | 100 | RET-ES | 5/5/5/5 | 0 | [0.0, 0.0] | four-realization sensitivity |
| counterfact | 100 | RET-GS | 5/5/5/5 | 0.60675 | [0.5559075774004048, 0.6575924225995953] | four-realization sensitivity |
| counterfact | 100 | LS | 5/5/5/5 | 0.857 | [0.7631133391210594, 0.9508866608789406] | four-realization sensitivity |
| counterfact | 300 | ES | 5/5/5/5 | -0.0001666667 | [-0.0006970743842140367, 0.0003637410508807067] | four-realization sensitivity |
| counterfact | 300 | RET-ES | 5/5/5/5 | -0.0006666667 | [-0.0015328188424168759, 0.00019948550908355624] | four-realization sensitivity |
| counterfact | 300 | RET-GS | 5/5/5/5 | 0.6174167 | [0.5836079417450792, 0.6512253915882542] | four-realization sensitivity |
| counterfact | 300 | LS | 5/5/5/5 | 0.972 | [0.972, 0.972] | four-realization sensitivity |
| counterfact | 1000 | ES | 5/5/5/5 | -0.0072 | [-0.00898141204449883, -0.005418587955501184] | four-realization sensitivity |
| counterfact | 1000 | RET-ES | 5/5/5/5 | -0.0235 | [-0.02844731383424808, -0.018552686165751963] | four-realization sensitivity |
| counterfact | 1000 | RET-GS | 5/5/5/5 | 0.562 | [0.5417991938506789, 0.5822008061493212] | four-realization sensitivity |
| counterfact | 1000 | LS | 5/5/5/5 | 0.975 | [0.9445303963834184, 1.0054696036165816] | four-realization sensitivity |


**Measured cost:** 70,447.439976 receipt-backed process seconds (19.568733 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## Upper-layer 2×2: reading upper features and writing only at the last tap

**Design and exposure.** DEC-073/077 cross all versus upper reader features with all versus last-only write taps, both datasets and three paired BP seeds, at exposed r0/order 100 through 300 edits. All twenty-four cells are complete; six full-read/full-write controls come from PC-reader. Reader training uses the full-write recipe; last-only writing is an evaluation intervention, not a separately trained last-write model. [I] [N]

**Reading and limits.** Last-only writing raises mean ordinary-text loss by roughly 2.64–4.37× in all twelve paired blocks while changing paraphrase retention little. Upper features do not establish that lower features are noise; the upper-trained CounterFact reader loses paraphrase retention in every seed, and one seed has notably poorer acquisition. Architecture, training and gating interactions constrain interpretation. The table separates write effects within each read/seed setting. [I]

Copied unchanged from [I] (line 14):

| Dataset | Seed | Read | Last−all RET-GS (pp) | Last−all mean ΔNLL | Mean-loss ratio |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | all | 0 | 0.0003100618 | 3.819539 |
| zsre | 0 | upper | 0 | 9.193163e-05 | 2.635521 |
| zsre | 1 | all | 0 | 0.0002989046 | 3.382472 |
| zsre | 1 | upper | 0 | 9.230497e-05 | 2.711768 |
| zsre | 2 | all | 0 | 0.0003898761 | 3.16521 |
| zsre | 2 | upper | 0 | 0.001149639 | 4.368299 |
| counterfact | 0 | all | -0.6666667 | 0.004619113 | 3.286399 |
| counterfact | 0 | upper | 0 | 0.002562541 | 2.972923 |
| counterfact | 1 | all | -0.3333333 | 0.01001728 | 2.87161 |
| counterfact | 1 | upper | -0.5 | 0.0009734975 | 3.301055 |
| counterfact | 2 | all | -0.5 | 0.002529835 | 3.138487 |
| counterfact | 2 | upper | -0.5 | 0.01504206 | 3.629792 |


**Measured cost:** 34,811.306527 receipt-backed process seconds (9.669807 hours), including this group's profiles and separate harm where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.


## HT-13: pooled frequency, severity and concentration

**Question, design and exposure.** The CPU reporting lanes following the DEC-074b halt describe all 270 receipted Stage-4 cells, using their saved full-position vectors against each model's own cap-off base. No new GPU experiment or subject is introduced. The native table below is the verified Round-63 refresh. [J] [P]

**Reading and limits.** Rare large losses can coexist with small averages. ES99+ is a fractional worst-1% average with zero mass retained, not the 99th percentile and not a positive-only conditional mean. The same positions are repeated across cells: pooled cell-position counts are not independent sample sizes. For S1, own cap-off means the continued base, not the original GPT-2. Concentration does not establish an asymptotic heavy-tail law. [J] [K]

Copied unchanged from [J] (line 1):

| condition | dataset | cells | changed positions | P(>0.01) | P(>1) | P(>5) | max (nats) | ES99+ | half-mass positions |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| learned reader (v5) | counterfact | 15 | 0.344 % | 0.2984 % | 0.1651 % | 0.0270 % | 15.38 | 0.571 | 1900 of 3678555 |
| learned reader (v5) | mquake | 15 | 0.355 % | 0.3133 % | 0.1941 % | 0.0226 % | 17.06 | 0.620 | 2336 of 3678555 |
| learned reader (v5) | zsre | 15 | 0.187 % | 0.1594 % | 0.0797 % | 0.0086 % | 11.05 | 0.260 | 1024 of 3678555 |
| random reader | counterfact | 15 | 2.167 % | 2.0450 % | 1.7049 % | 0.5219 % | 20.28 | 5.528 | 18856 of 3678555 |
| random reader | mquake | 15 | 0.431 % | 0.4089 % | 0.3357 % | 0.0686 % | 15.07 | 1.224 | 3818 of 3678555 |
| random reader | zsre | 15 | 0.029 % | 0.0266 % | 0.0173 % | 0.0010 % | 7.00 | 0.048 | 225 of 3678555 |
| continued base (LM) + stable cap | counterfact | 15 | 0.000 % | 0.0000 % | 0.0000 % | 0.0000 % | 0.00 | 0.000 | 0 of 3678555 |
| continued base (LM) + stable cap | zsre | 15 | 0.172 % | 0.1049 % | 0.0335 % | 0.0096 % | 27.61 | 0.181 | 266 of 3678555 |
| continued base (literal) + stable cap | zsre | 15 | 0.171 % | 0.1041 % | 0.0337 % | 0.0094 % | 27.69 | 0.179 | 263 of 3678555 |
| matched update | counterfact | 15 | 0.000 % | 0.0000 % | 0.0000 % | 0.0000 % | 0.00 | 0.000 | 0 of 3678555 |
| matched update | zsre | 15 | 0.169 % | 0.1053 % | 0.0338 % | 0.0092 % | 33.77 | 0.177 | 280 of 3678555 |
| live v0 cap C1 | counterfact | 15 | 0.000 % | 0.0000 % | 0.0000 % | 0.0000 % | 0.00 | 0.000 | 0 of 3678555 |
| live v0 cap C1 | zsre | 15 | 0.144 % | 0.0959 % | 0.0458 % | 0.0125 % | 27.68 | 0.210 | 497 of 3678555 |
| live v0 cap C2 | counterfact | 15 | 0.000 % | 0.0000 % | 0.0000 % | 0.0000 % | 0.00 | 0.000 | 0 of 3678555 |
| live v0 cap C2 | zsre | 15 | 0.021 % | 0.0187 % | 0.0160 % | 0.0150 % | 50.60 | 0.321 | 175 of 3678555 |
| stable v0 cap | counterfact | 15 | 0.000 % | 0.0000 % | 0.0000 % | 0.0000 % | 0.00 | 0.000 | 0 of 3678555 |
| stable v0 cap | mquake | 15 | 0.000 % | 0.0000 % | 0.0000 % | 0.0000 % | 0.00 | 0.000 | 0 of 3678555 |
| stable v0 cap | zsre | 15 | 0.170 % | 0.1041 % | 0.0335 % | 0.0094 % | 27.68 | 0.179 | 262 of 3678555 |


**Post-halt GPU charge:** none added for this saved-result analysis or historical pilot. CPU refresh durations and known historical pilot costs remain separately catalogued in [O] [X].


## HT-15: cell-level and realization spread

**Question, design and exposure.** The post-halt HT-15b reporting lane asks how much the pooled result varies across the same 270 completed cells, with three realizations and five dependent orders per group. The table retains every observed condition/dataset, including S1_literal zsRE's fifteen completed cells. [K] [P]

**Reading and limits.** Compute the cell statistic first, then average five orders within each realization. Realization ranges are descriptive, not confidence intervals; pooled ES99 and mean cell ES99 are different estimands. MQuAKE ends at 300 edits; its rows do not imply 1,000-edit evidence. Unrun conditions are absent evidence, not zero harm. These lanes consume saved results and have zero additional GPU cost. [K]

Copied unchanged from [K] (line 7):

| Condition | Dataset | Cells / 15 | Metric | Mean over observed cells | r0 (n) | r1 (n) | r2 (n) | Full r range |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| R1_learned_ff | counterfact | 15 | mean_signed | 0.00549791 | 0.00584963 (5) | 0.0046208 (5) | 0.00602332 (5) | 0.0046208 to 0.00602332 |
| R1_learned_ff | counterfact | 15 | es99_positive | 0.570613 | 0.61007 (5) | 0.479876 (5) | 0.621891 (5) | 0.479876 to 0.621891 |
| R1_learned_ff | counterfact | 15 | maximum | 13.5928 | 15.3818 (5) | 11.3658 (5) | 14.0308 (5) | 11.3658 to 15.3818 |
| R1_learned_ff | counterfact | 15 | exceed_0.01 | 0.00298351 | 0.00298079 (5) | 0.00263419 (5) | 0.00333555 (5) | 0.00263419 to 0.00333555 |
| R1_learned_ff | counterfact | 15 | exceed_1 | 0.00165146 | 0.00168001 (5) | 0.00145573 (5) | 0.00181865 (5) | 0.00145573 to 0.00181865 |
| R1_learned_ff | counterfact | 15 | exceed_5 | 0.000270487 | 0.000326215 (5) | 0.000207962 (5) | 0.000277283 (5) | 0.000207962 to 0.000326215 |
| R1_learned_ff | counterfact | 15 | half_mass_positions | 127.667 | 123 (5) | 114 (5) | 146 (5) | 114 to 146 |
| R1_learned_ff | mquake | 15 | mean_signed | 0.00607367 | 0.00714616 (5) | 0.00693902 (5) | 0.00413585 (5) | 0.00413585 to 0.00714616 |
| R1_learned_ff | mquake | 15 | es99_positive | 0.620475 | 0.730636 (5) | 0.710095 (5) | 0.420694 (5) | 0.420694 to 0.730636 |
| R1_learned_ff | mquake | 15 | maximum | 13.486 | 13.1443 (5) | 17.0605 (5) | 10.2532 (5) | 10.2532 to 17.0605 |
| R1_learned_ff | mquake | 15 | exceed_0.01 | 0.00313302 | 0.00362099 (5) | 0.00348235 (5) | 0.00229574 (5) | 0.00229574 to 0.00362099 |
| R1_learned_ff | mquake | 15 | exceed_1 | 0.00194098 | 0.00223865 (5) | 0.0021938 (5) | 0.00139049 (5) | 0.00139049 to 0.00223865 |
| R1_learned_ff | mquake | 15 | exceed_5 | 0.000225632 | 0.000256894 (5) | 0.000289516 (5) | 0.000130486 (5) | 0.000130486 to 0.000289516 |
| R1_learned_ff | mquake | 15 | half_mass_positions | 156.667 | 185 (5) | 171 (5) | 114 (5) | 114 to 185 |
| R1_learned_ff | zsre | 15 | mean_signed | 0.00248586 | 0.00245023 (5) | 0.00255302 (5) | 0.00245432 (5) | 0.00245023 to 0.00255302 |
| R1_learned_ff | zsre | 15 | es99_positive | 0.259815 | 0.258806 (5) | 0.266315 (5) | 0.254325 (5) | 0.254325 to 0.266315 |
| R1_learned_ff | zsre | 15 | maximum | 9.75467 | 9.26227 (5) | 8.95399 (5) | 11.0477 (5) | 8.95399 to 11.0477 |
| R1_learned_ff | zsre | 15 | exceed_0.01 | 0.00159438 | 0.00161069 (5) | 0.00163923 (5) | 0.00153321 (5) | 0.00153321 to 0.00163923 |
| R1_learned_ff | zsre | 15 | exceed_1 | 0.000796508 | 0.000803305 (5) | 0.000815538 (5) | 0.000770683 (5) | 0.000770683 to 0.000815538 |
| R1_learned_ff | zsre | 15 | exceed_5 | 8.56315e-05 | 8.56315e-05 (5) | 0.000101942 (5) | 6.93207e-05 (5) | 6.93207e-05 to 0.000101942 |
| R1_learned_ff | zsre | 15 | half_mass_positions | 68.6667 | 69 (5) | 70 (5) | 67 (5) | 67 to 70 |
| R1_nonlearned | counterfact | 15 | mean_signed | 0.0706286 | 0.0595273 (5) | 0.0882374 (5) | 0.0641211 (5) | 0.0595273 to 0.0882374 |
| R1_nonlearned | counterfact | 15 | es99_positive | 5.45373 | 5.02336 (5) | 6.14514 (5) | 5.19268 (5) | 5.02336 to 6.14514 |
| R1_nonlearned | counterfact | 15 | maximum | 18.0114 | 20.2834 (5) | 17.4515 (5) | 16.2994 (5) | 16.2994 to 20.2834 |
| R1_nonlearned | counterfact | 15 | exceed_0.01 | 0.0204499 | 0.0180446 (5) | 0.0234182 (5) | 0.0198869 (5) | 0.0180446 to 0.0234182 |
| R1_nonlearned | counterfact | 15 | exceed_1 | 0.0170488 | 0.0147653 (5) | 0.0202865 (5) | 0.0160946 (5) | 0.0147653 to 0.0202865 |
| R1_nonlearned | counterfact | 15 | exceed_5 | 0.00521944 | 0.00410215 (5) | 0.00704217 (5) | 0.004514 (5) | 0.00410215 to 0.00704217 |
| R1_nonlearned | counterfact | 15 | half_mass_positions | 1259.33 | 1077 (5) | 1552 (5) | 1149 (5) | 1077 to 1552 |
| R1_nonlearned | mquake | 15 | mean_signed | 0.0121018 | 0.0120472 (5) | 0.0120871 (5) | 0.0121709 (5) | 0.0120472 to 0.0121709 |
| R1_nonlearned | mquake | 15 | es99_positive | 1.22449 | 1.21908 (5) | 1.22397 (5) | 1.23044 (5) | 1.21908 to 1.23044 |
| R1_nonlearned | mquake | 15 | maximum | 14.239 | 15.0722 (5) | 12.7709 (5) | 14.8738 (5) | 12.7709 to 15.0722 |
| R1_nonlearned | mquake | 15 | exceed_0.01 | 0.00408856 | 0.00414293 (5) | 0.00404914 (5) | 0.00407361 (5) | 0.00404914 to 0.00414293 |
| R1_nonlearned | mquake | 15 | exceed_1 | 0.0033573 | 0.00337225 (5) | 0.00333555 (5) | 0.00336409 (5) | 0.00333555 to 0.00337225 |
| R1_nonlearned | mquake | 15 | exceed_5 | 0.000686411 | 0.000701362 (5) | 0.000701362 (5) | 0.000656508 (5) | 0.000656508 to 0.000701362 |
| R1_nonlearned | mquake | 15 | half_mass_positions | 255 | 254 (5) | 258 (5) | 253 (5) | 253 to 258 |
| R1_nonlearned | zsre | 15 | mean_signed | 0.000469895 | 0.000316561 (5) | 0.000716578 (5) | 0.000376546 (5) | 0.000316561 to 0.000716578 |
| R1_nonlearned | zsre | 15 | es99_positive | 0.0481189 | 0.0324633 (5) | 0.0735695 (5) | 0.038324 (5) | 0.0324633 to 0.0735695 |
| R1_nonlearned | zsre | 15 | maximum | 6.16107 | 5.66083 (5) | 7.00099 (5) | 5.82137 (5) | 5.66083 to 7.00099 |
| R1_nonlearned | zsre | 15 | exceed_0.01 | 0.000266409 | 0.000216117 (5) | 0.000395536 (5) | 0.000187574 (5) | 0.000187574 to 0.000395536 |
| R1_nonlearned | zsre | 15 | exceed_1 | 0.000172622 | 0.000114175 (5) | 0.000248739 (5) | 0.000154952 (5) | 0.000114175 to 0.000248739 |
| R1_nonlearned | zsre | 15 | exceed_5 | 9.51461e-06 | 4.07769e-06 (5) | 2.03884e-05 (5) | 4.07769e-06 (5) | 4.07769e-06 to 2.03884e-05 |
| R1_nonlearned | zsre | 15 | half_mass_positions | 15.6667 | 12 (5) | 22 (5) | 13 (5) | 12 to 22 |
| S1_LM | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| S1_LM | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| S1_LM | zsre | 15 | mean_signed | 0.00155872 | 0.00108663 (5) | 0.0019292 (5) | 0.00166032 (5) | 0.00108663 to 0.0019292 |
| S1_LM | zsre | 15 | es99_positive | 0.180511 | 0.132904 (5) | 0.216925 (5) | 0.191705 (5) | 0.132904 to 0.216925 |
| S1_LM | zsre | 15 | maximum | 25.3032 | 26.9174 (5) | 26.2938 (5) | 22.6986 (5) | 22.6986 to 26.9174 |
| S1_LM | zsre | 15 | exceed_0.01 | 0.00104933 | 0.00100148 (5) | 0.00114501 (5) | 0.00100148 (5) | 0.00100148 to 0.00114501 |
| S1_LM | zsre | 15 | exceed_1 | 0.000335458 | 0.000247923 (5) | 0.00034905 (5) | 0.0004094 (5) | 0.000247923 to 0.0004094 |
| S1_LM | zsre | 15 | exceed_5 | 9.59616e-05 | 5.79032e-05 (5) | 0.000127224 (5) | 0.000102758 (5) | 5.79032e-05 to 0.000127224 |
| S1_LM | zsre | 15 | half_mass_positions | 19.4 | 15 (5) | 19.8 (5) | 23.4 (5) | 15 to 23.4 |
| S1_literal | zsre | 15 | mean_signed | 0.00154643 | 0.00108576 (5) | 0.00189067 (5) | 0.00166286 (5) | 0.00108576 to 0.00189067 |
| S1_literal | zsre | 15 | es99_positive | 0.179436 | 0.132983 (5) | 0.21308 (5) | 0.192244 (5) | 0.132983 to 0.21308 |
| S1_literal | zsre | 15 | maximum | 25.3237 | 26.951 (5) | 26.3442 (5) | 22.6758 (5) | 22.6758 to 26.951 |
| S1_literal | zsre | 15 | exceed_0.01 | 0.0010409 | 0.00100393 (5) | 0.0011336 (5) | 0.000985169 (5) | 0.000985169 to 0.0011336 |
| S1_literal | zsre | 15 | exceed_1 | 0.000337089 | 0.000251186 (5) | 0.000351497 (5) | 0.000408584 (5) | 0.000251186 to 0.000408584 |
| S1_literal | zsre | 15 | exceed_5 | 9.40587e-05 | 5.70876e-05 (5) | 0.000123962 (5) | 0.000101127 (5) | 5.70876e-05 to 0.000123962 |
| S1_literal | zsre | 15 | half_mass_positions | 19.1333 | 15.2 (5) | 19.4 (5) | 22.8 (5) | 15.2 to 22.8 |
| matched_update | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| matched_update | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| matched_update | zsre | 15 | mean_signed | 0.00151316 | 0.00105644 (5) | 0.0017856 (5) | 0.00169745 (5) | 0.00105644 to 0.0017856 |
| matched_update | zsre | 15 | es99_positive | 0.176639 | 0.130173 (5) | 0.204576 (5) | 0.195167 (5) | 0.130173 to 0.204576 |
| matched_update | zsre | 15 | maximum | 22.1265 | 24.6112 (5) | 21.5077 (5) | 20.2605 (5) | 20.2605 to 24.6112 |
| matched_update | zsre | 15 | exceed_0.01 | 0.00105313 | 0.00102595 (5) | 0.00111158 (5) | 0.00102187 (5) | 0.00102187 to 0.00111158 |
| matched_update | zsre | 15 | exceed_1 | 0.000338448 | 0.000251186 (5) | 0.000346603 (5) | 0.000417555 (5) | 0.000251186 to 0.000417555 |
| matched_update | zsre | 15 | exceed_5 | 9.21558e-05 | 6.36119e-05 (5) | 0.000106835 (5) | 0.00010602 (5) | 6.36119e-05 to 0.000106835 |
| matched_update | zsre | 15 | half_mass_positions | 20.4667 | 17.6 (5) | 19.8 (5) | 24 (5) | 17.6 to 24 |
| v0_live_C1 | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C1 | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_live_C1 | zsre | 15 | mean_signed | 0.00189612 | 0.00143227 (5) | 0.00261712 (5) | 0.00163895 (5) | 0.00143227 to 0.00261712 |
| v0_live_C1 | zsre | 15 | es99_positive | 0.209756 | 0.162794 (5) | 0.277351 (5) | 0.189121 (5) | 0.162794 to 0.277351 |
| v0_live_C1 | zsre | 15 | maximum | 19.3169 | 26.9542 (5) | 12.2902 (5) | 18.7064 (5) | 12.2902 to 26.9542 |
| v0_live_C1 | zsre | 15 | exceed_0.01 | 0.0009588 | 0.000870179 (5) | 0.00105286 (5) | 0.000953363 (5) | 0.000870179 to 0.00105286 |
| v0_live_C1 | zsre | 15 | exceed_1 | 0.000457788 | 0.000291962 (5) | 0.000649168 (5) | 0.000432235 (5) | 0.000291962 to 0.000649168 |
| v0_live_C1 | zsre | 15 | exceed_5 | 0.000125321 | 8.07382e-05 (5) | 0.000181049 (5) | 0.000114175 (5) | 8.07382e-05 to 0.000181049 |
| v0_live_C1 | zsre | 15 | half_mass_positions | 34.5333 | 18.6 (5) | 54.6 (5) | 30.4 (5) | 18.6 to 54.6 |
| v0_live_C2 | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_live_C2 | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_live_C2 | zsre | 15 | mean_signed | 0.00319807 | 0.00241095 (5) | 0.0034409 (5) | 0.00374234 (5) | 0.00241095 to 0.00374234 |
| v0_live_C2 | zsre | 15 | es99_positive | 0.32128 | 0.242571 (5) | 0.345971 (5) | 0.375299 (5) | 0.242571 to 0.375299 |
| v0_live_C2 | zsre | 15 | maximum | 43.1129 | 38.7553 (5) | 41.1178 (5) | 49.4658 (5) | 38.7553 to 49.4658 |
| v0_live_C2 | zsre | 15 | exceed_0.01 | 0.000186758 | 0.00017371 (5) | 0.00017371 (5) | 0.000212855 (5) | 0.00017371 to 0.000212855 |
| v0_live_C2 | zsre | 15 | exceed_1 | 0.000159574 | 0.00014435 (5) | 0.00014435 (5) | 0.00019002 (5) | 0.00014435 to 0.00019002 |
| v0_live_C2 | zsre | 15 | exceed_5 | 0.000150331 | 0.00012967 (5) | 0.000140272 (5) | 0.000181049 (5) | 0.00012967 to 0.000181049 |
| v0_live_C2 | zsre | 15 | half_mass_positions | 12.5333 | 10.8 (5) | 12.6 (5) | 14.2 (5) | 10.8 to 14.2 |
| v0_stable | counterfact | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | counterfact | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_stable | mquake | 15 | mean_signed | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | es99_positive | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | maximum | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | exceed_0.01 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | exceed_1 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | exceed_5 | 0 | 0 (5) | 0 (5) | 0 (5) | 0 to 0 |
| v0_stable | mquake | 15 | half_mass_positions | undefined / incomplete | undefined / incomplete (5) | undefined / incomplete (5) | undefined / incomplete (5) | — |
| v0_stable | zsre | 15 | mean_signed | 0.00154124 | 0.00108652 (5) | 0.00189493 (5) | 0.00164227 (5) | 0.00108652 to 0.00189493 |
| v0_stable | zsre | 15 | es99_positive | 0.178654 | 0.132148 (5) | 0.213499 (5) | 0.190313 (5) | 0.132148 to 0.213499 |
| v0_stable | zsre | 15 | maximum | 25.3134 | 26.9542 (5) | 26.2876 (5) | 22.6985 (5) | 22.6985 to 26.9542 |
| v0_stable | zsre | 15 | exceed_0.01 | 0.0010409 | 0.000999034 (5) | 0.00113278 (5) | 0.000990878 (5) | 0.000990878 to 0.00113278 |
| v0_stable | zsre | 15 | exceed_1 | 0.000334914 | 0.000247923 (5) | 0.000349866 (5) | 0.000406953 (5) | 0.000247923 to 0.000406953 |
| v0_stable | zsre | 15 | exceed_5 | 9.43305e-05 | 5.70876e-05 (5) | 0.000123962 (5) | 0.000101942 (5) | 5.70876e-05 to 0.000123962 |
| v0_stable | zsre | 15 | half_mass_positions | 19 | 15 (5) | 19.2 (5) | 22.8 (5) | 15 to 22.8 |


**Post-halt GPU charge:** none added for this saved-result analysis or historical pilot. CPU refresh durations and known historical pilot costs remain separately catalogued in [O] [X].


## HT-17: saved-vector finite-range tail analysis

**Question, design and exposure.** DEC-081a authorizes CPU-only analysis separating the probability of Δ>.01 from its conditional severity and from gate firing, then comparing generalized-Pareto excess fits with exponential fits on held-out windows. The final snapshot has 303 cells: 225 Stage-4 zsRE/CounterFact, 30 AW-B, twelve PC-reader and 36 legacy pilot. AW-L and Option R are outside this fit inventory. The source's old generic sentence about a pending reader comparison does not override its zero-pending, twelve-reader-cell inventory or the final reader report [G]. [L] [S] [N]

**Reading and limits.** Fits concern observed finite ranges, not complexity classes, accessible-state growth W(N), infinite variance or measured temperature. Fitted learned-reader shapes show little held-out advantage over exponential; invalid/sparse fits stay invalid, including likelihood endpoints and shapes outside the declared entropy domain. This does not weaken AW-B's analytic ceiling. Joint window resampling conditions on the fixed cells; it does not measure new-subject uncertainty. Full 1,931-window and legacy 32-window populations are never merged. Historical pilot MQuAKE retention and drift populations differ. Complete fits, diagnostics and intervals remain in [L]; the accessible interpretation is [Y]. [N]

Copied unchanged from [L] (line 17):

| Study | Dataset | Condition | Cells | P(Δ>.01) [interval] | Mean Δ given >.01 [interval] | Gate-selected fraction | ES99+ | Max range | RET-GS |
|---|---|---|---:|---|---|---:|---:|---|---:|
| AW-B | counterfact | capoff | 5 | 0 [0 to 0] | — [—] | 0.0034978 | 0 | 0 to 0 | 0 |
| AW-B | counterfact | mixture:0.367879 | 5 | 0.0030517 [0.0027963 to 0.003307] | 0.58109 [0.56386 to 0.60015] | 0.0034978 | 0.17735 | 0.99999 to 1 | 0.757 |
| AW-B | counterfact | v5 | 5 | 0.0030583 [0.0028028 to 0.0033121] | 1.9252 [1.8199 to 2.0498] | 0.0034978 | 0.5888 | 11.744 to 15.382 | 0.767 |
| AW-B | zsre | capoff | 5 | 0 [0 to 0] | — [—] | 0.0014362 | 0 | 0 to 0 | 0 |
| AW-B | zsre | mixture:0.367879 | 5 | 0.0011809 [0.0010243 to 0.0013532] | 0.54217 [0.518 to 0.56501] | 0.0014362 | 0.064035 | 0.99957 to 0.99999 | 0.984 |
| AW-B | zsre | v5 | 5 | 0.0011874 [0.0010323 to 0.0013584] | 1.6189 [1.5083 to 1.7592] | 0.0014362 | 0.19224 | 8.3038 to 12.293 | 0.984 |
| PC-reader | counterfact | bp | 3 | 0.0012668 [0.0011075 to 0.0014354] | 2.313 [2.1342 to 2.4936] | 0.0014476 | 0.29301 | 8.5193 to 12.502 | 0.815 |
| PC-reader | counterfact | epc | 3 | 0.0014802 [0.0013114 to 0.0016531] | 2.2064 [1.996 to 2.3879] | 0.0017099 | 0.3266 | 7.706 to 12.624 | 0.66889 |
| PC-reader | zsre | bp | 3 | 6.2525e-05 [4.3461e-05 to 8.434e-05] | 2.28 [1.6698 to 2.9691] | 7.068e-05 | 0.014255 | 6.5063 to 10.576 | 0.98 |
| PC-reader | zsre | epc | 3 | 5.4369e-06 [1.3592e-06 to 1.0874e-05] | 2.971 [—] | 8.1554e-06 | 0.0016153 | 0 to 4.4497 | 0.96556 |
| kappa-pilot | counterfact | clip2 | 3 | 0.0054134 [0.0019685 to 0.0098487] | 2.4857 [1.7126 to 3.4442] | — | 1.3457 | 6.4299 to 6.5609 | 0.75333 |
| kappa-pilot | counterfact | kappa02 | 3 | 0.0042651 [0.00065617 to 0.0080565] | 2.4632 [1.8862 to 3.4358] | — | 1.0507 | 5.0747 to 6.4554 | 0.76667 |
| kappa-pilot | counterfact | kappa05 | 3 | 0.0027067 [0.00073204 to 0.0056656] | 2.773 [1.7023 to 4.4671] | — | 0.75066 | 4.4563 to 6.4554 | 0.71 |
| kappa-pilot | counterfact | ordinary | 3 | 0.0082841 [0.0021305 to 0.016412] | 2.2162 [1.6933 to 2.8086] | — | 1.713 | 5.491 to 6.4554 | 0.775 |
| kappa-pilot | mquake | clip2 | 3 | 0.0011483 [0 to 0.0025529] | 1.7604 [—] | — | 0.20226 | 1.1538 to 6.9388 | 0.66667 |
| kappa-pilot | mquake | kappa02 | 3 | 0.0023786 [8.2021e-05 to 0.0054318] | 0.85218 [—] | — | 0.2028 | 1.2338 to 2.9896 | 0.57 |
| kappa-pilot | mquake | kappa05 | 3 | 0.0018865 [0 to 0.0041872] | 1.0619 [—] | — | 0.20042 | 1.0783 to 3.7785 | 0.61667 |
| kappa-pilot | mquake | ordinary | 3 | 0.0058235 [0.0015563 to 0.010343] | 1.2272 [0.76366 to 2.0118] | — | 0.71437 | 2.0764 to 6.9388 | 0.64667 |
| kappa-pilot | zsre | clip2 | 3 | 0 [0 to 0] | — [—] | — | 0.00012318 | 0.00016735 to 0.00016735 | 0.91667 |
| kappa-pilot | zsre | kappa02 | 3 | 0 [0 to 0] | — [—] | — | 0.00012318 | 0.00016735 to 0.00016735 | 0.92667 |
| kappa-pilot | zsre | kappa05 | 3 | 0 [0 to 0] | — [—] | — | 0.00012318 | 0.00016735 to 0.00016735 | 0.91667 |
| kappa-pilot | zsre | ordinary | 3 | 0.0027067 [0.0011483 to 0.0042671] | 2.9261 [2.0577 to 3.7217] | — | 0.7921 | 0.00016735 to 8.686 | 0.96667 |
| stage4 | counterfact | R1_learned_ff | 15 | 0.0029835 [0.0026987 to 0.0033119] | 1.9125 [1.7877 to 2.0385] | — | 0.57061 | 11.366 to 15.382 | 0.678 |
| stage4 | counterfact | R1_nonlearned | 15 | 0.02045 [0.019808 to 0.021014] | 3.4865 [3.4311 to 3.5434] | — | 5.4537 | 16.299 to 20.283 | 0.1205 |
| stage4 | counterfact | S1_LM | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | matched_update | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | v0_live_C1 | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | v0_live_C2 | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | v0_stable | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | zsre | R1_learned_ff | 15 | 0.0015944 [0.001366 to 0.0018256] | 1.6295 [1.4921 to 1.7773] | — | 0.25982 | 8.954 to 11.048 | 0.96033 |
| stage4 | zsre | R1_nonlearned | 15 | 0.00026641 [0.00021476 to 0.00031677] | 1.8062 [1.5691 to 2.0404] | — | 0.048119 | 5.6608 to 7.001 | 0.524 |
| stage4 | zsre | S1_LM | 15 | 0.0010493 [0.00096798 to 0.0011211] | 1.7202 [1.5195 to 1.9585] | — | 0.18051 | 19.362 to 27.605 | 0.1866 |
| stage4 | zsre | S1_literal | 15 | 0.0010409 [0.00096228 to 0.0011117] | 1.7238 [1.5254 to 1.9448] | — | 0.17944 | 19.344 to 27.688 | 0.18873 |
| stage4 | zsre | matched_update | 15 | 0.0010531 [0.00097558 to 0.0011195] | 1.6772 [1.4921 to 1.8631] | — | 0.17664 | 17.085 to 33.767 | 0.18367 |
| stage4 | zsre | v0_live_C1 | 15 | 0.0009588 [0.00088046 to 0.0010298] | 2.1876 [2.0116 to 2.3972] | — | 0.20976 | 10.426 to 27.684 | 0.1304 |
| stage4 | zsre | v0_live_C2 | 15 | 0.00018676 [0.00016011 to 0.0002175] | 17.203 [15.705 to 18.744] | — | 0.32128 | 38.755 to 50.597 | 0.10727 |
| stage4 | zsre | v0_stable | 15 | 0.0010409 [0.0009596 to 0.0011103] | 1.7163 [1.519 to 1.9331] | — | 0.17865 | 19.339 to 27.684 | 0.1856 |


**Post-halt GPU charge:** none added for this saved-result analysis or historical pilot. CPU refresh durations and known historical pilot costs remain separately catalogued in [O] [X].


## Legacy κ pilot: a bounded surprisal loss

**Question, design and exposure.** DEC-054 authorized κ=.2/.5 and clip-2 against reused ordinary v5-family readers, three seeds each, on the older development populations. All 36 endpoint rows are complete. This September-16 experiment predates the halt; it is included for the scientific narrative, not charged to the new portfolio. For surprisal ℓ, the implemented loss is (1−exp(−κℓ))/κ. [M] [N] [W]

**Reading and limits.** Both κ arms fail the prespecified retention floor and neither tail reduction exceeds the ordinary seed-spread criterion. The clipped control shares κ=.5's ceiling, not κ=.2's; it is not evidence for a κ-specific advantage. ES95 here is different from the ES99 measure above. These are preliminary hints, not the coupled free energy (no coupled expectation or changed inference distribution), not a coupled Markov blanket, and not a test of a shared κ for porosity and interference. Its null does not test the unimplemented coupled objective (DEC-081a). Nine new trainings and endpoint evaluations have partial measured receipts, but historical drift assays lack enclosing durations: a complete pilot GPU total is unavailable, not zero. The receipt catalog and reproduction guide retain the known components. [M] [N] [O] [X]

Copied unchanged from [M] (line 54):

| Arm | RET-GS macro | ES95 seed macros | ES95 macro | Maximum seed macros | Maximum macro |
|---|---:|---|---:|---|---:|
| ordinary | 0.796111111 | 0.450433221, 0.0629618065, 0.155370232 | 0.222921753 | 6.96185085, 2.52254184, 6.30664826 | 5.26368032 |
| kappa02 | 0.754444444 | 0.0431188349, 0.146847777, 0.060939565 | 0.0836353922 | 2.10287433, 3.14839457, 2.85126749 | 2.70084546 |
| kappa05 | 0.747777778 | 0.0620028719, 0.03745967, 0.0909653852 | 0.0634759757 | 2.50278088, 1.89676677, 3.41137163 | 2.60363976 |
| clip2 | 0.778888889 | 0.0989111328, 0.145672496, 0.0652129828 | 0.103265537 | 3.82595653, 4.49994573, 2.53646947 | 3.62079058 |


**Post-halt GPU charge:** none added for this saved-result analysis or historical pilot. CPU refresh durations and known historical pilot costs remain separately catalogued in [O] [X].


## Measured post-halt compute: receipts, scope and missing costs

**Verified nonoverlapping total: 549,768.871787 process seconds = 152.713575 process-hours across 101 enclosing receipts.** There are 3 additional logged failed launches with unknown durations, so this is a **lower bound on total process spend**, not a complete bill. These are elapsed wall durations of GPU-bound processes, including compilation/CPU work; they are neither CUDA-kernel time nor elapsed exclusive GPU occupancy.

| Work (profiles included) | Known process seconds | Process hours |
| --- | --- | --- |
| AW-B calibration | 19467.922026 | 5.407756 |
| AW-B evaluation | 21083.166993 | 5.856435 |
| AW-L new work | 34811.306527 | 9.669807 |
| Fixed-v5 default | 6921.982280 | 1.922773 |
| Fixed-v5 settings | 21189.820529 | 5.886061 |
| Option R | 70447.439976 | 19.568733 |
| PC-reader | 286632.424427 | 79.620118 |
| PC-v0 default | 51429.816123 | 14.286060 |
| PC-v0 depth 1 | 9754.313701 | 2.709532 |
| PC-v0 depth 32 | 13777.226031 | 3.827007 |
| PC-v0 offered-budget | 9023.390972 | 2.506497 |
| PC-v0 random | 5230.062203 | 1.452795 |

Each PC driver summary encloses its serial child cells. Each harm receipt encloses its arm readouts. PC-reader/AW-L training and evaluation receipts include their nested stream/harm durations. Shared full-read BP controls are charged to PC-reader once; AW-L's attributed total includes them and is deliberately not summed. Option R charges child dispatch receipts, including the ceiling stop; closed-session elapsed time and nested driver times are not added. Failed numerical-table formatting on the default fixed-v5 harm run remains charged and failed.

Excluded: the pre-release September-26 diagnostic refused an occupied GPU before model work; PC12 and named CPU smokes are fixtures; L0/L1/PC-4/PC-6 are CPU checks; the original Stage-4 run and September-16 κ pilot predate the halt. Repeated reporting/fit/figure refreshes are CPU costs. The scope is the closed supplemental portfolio's preserved receipts, not every process on the host.

**Missing durations:** initial fixed-v5 k32, lr .05 and lr .2 harm launch logs show failures before their successful retries. k32 failed input validation; the rate variants reached model/readout setup. The successful retry receipts cannot stand in for those earlier durations. No estimate or zero has been substituted, and no claimed ceiling overrun follows from the known total alone.

## What the programme supports, and what it does not

**Predictive coding:** corrected error settling has now been tested in acquisition and in reader training. Its effects depend on substrate, endpoint and compute; no general superiority or biological locality follows. The original ePC-50M/v0 experiment must remain separate from GPT-2-small/v5. [A] [D] [G]

**Heavy-tailed distributions:** the data demonstrate rare, concentrated harm and finite-range tail behavior. They do not establish an asymptotic heavy-tail class, infinite variance, an entropy measurement, or the growth of accessible states. The mixture ceiling is an algebraic bound on the measured token observable, not a fitted class transition. The κ loss pilot tests a bounded deformation of surprisal, not the untested coupled-entropy/free-energy proposal. This follows the approved DEC-081a wording. [L] [M] [N]

**Active inference in the Extremes:** selective correction and its costs are a useful experimental substrate for an active-inference programme. Autonomous expected-free-energy policy selection, an informational coupled-free-energy objective, and a validated κ-porous/Markov-blanket interpretation remain proposed work. No equation has been selected as that future training objective. DEC-082 retains those questions for post-conference collaboration; the optional extra κ readout and 3,000-edit scaling study are closed without execution. [N]

**Generalization:** GPT-2-small (124M parameters), English benchmark editing, limited subject draws, exposed evaluations and dependent text positions do not establish behavior in larger or deployed systems. The original v0 PC substrate is smaller still. Training seeds, stream orders, windows and subject realizations are different units of variation. Better prompt retention is not equivalent to factual correctness, safety or overall model fidelity. [P] [G] [L]

## Remaining work and schedule

DEC-083 closes the GPU portfolio: the last GPU step finished October 4 at 01:17. No new fits are planned. The October-6 freeze dry run, final source/audit refresh, lead's October-9 17:00 EDT freeze, and preparation for the October-15 presentation remain. The freeze checklist [Q] assigns the lead's signature; this report is not that signature. Colleague-talk revisions await charlie's rehearsal feedback. [N] [Q]


## Reproduction and source registry

Run `../venv/bin/python -m aw.additional_work_assembly --output NEW_DIRECTORY --document NEW_REPORT.md` from pc_cap. Both destinations must be new. This uses saved documents/receipts only; no model imports, scoring or fitting. `assembly.json` binds copied table bytes, the report, producers and receipt ledger. X25 checks this assembly alongside the native reports. The October-6 full freeze refresh remains a separate task.


[A]: additional_work/PC-v0_report.md "SHA256 447b04f24175792c755fa6f7793c2eaa592036477e365fbcf52c45cc5c5f173b"

[B]: additional_work/PC-controls_report.md "SHA256 428a50efff6048ecaf3b31ec19e5d27fe5cf6bf1741012ba394bc831c0e1e117"

[C]: additional_work/PC-matched-control_report.md "SHA256 9336afdade0993fdbd92d9e1ca4b43a47048ccdae0033b8ed315e819802c3993"

[D]: additional_work/PC-v1_report.md "SHA256 294c8941a26891eda117b3878cc4a47421c1d81d2315cb6a4772bcb6d024e7bb"

[E]: ../logs/additional_work/reproductions/round63-verified/documents/PC-settings_report.md "SHA256 7256ab5154bcb676c5513aea56e95aaf4d04a6bafe419462cd1953301fcacf3d"

[F]: additional_work/AW-B_report.md "SHA256 0a636148f6933a89552e57e9db368300ffd9a1874fdb6d67b577eb6899c8c150"

[G]: additional_work/PC-reader_report.md "SHA256 b871d4033bc2cd7a0a01add3563d0357f6a7fd9b71b8cd379ac918077601a707"

[H]: additional_work/R_report.md "SHA256 a75935a11e139c36ecd63ec1d70d32caa64fdb5ebb88df0cb80ed78d0d7b3364"

[I]: additional_work/AW-L_report.md "SHA256 9b2de526da9d92144a7efc456fc0dbbe6837de2ee59b89049460a35fc9de2f28"

[J]: ../../assets/presentation-materials/reproductions/round63-verified/ht13/table.md "SHA256 68ce0923d3a009174c769b3a26ca71195962ec64b2133c159e61b15b2d0a957f"

[K]: ../logs/additional_work/round48/HT-15b-270/tail_spread.md "SHA256 442a2dd5339fa0c91ccf5247ee5b39a0259a3062f6e5d824ab6855d9cc7ab792"

[L]: ../logs/additional_work/HT-17/snapshot-20261004-complete/report.md "SHA256 e8b5d4eb810150314025ffd29925d3ff85367780c1994a8f3f017eb8f101bc7c"

[M]: ../logs/r1_round18/ht3d-pilot-final-aliases.md "SHA256 20c911b3f416839b2a47c2702815f6f855335f7ad1df6ff29f9354999de72e6d"

[N]: decisions.md "SHA256 25f4f95524df9065957b7dec879ee57ad2503426ab06ad0124e24defe32983a7"

[O]: REPRODUCE_additional_work.md "SHA256 5a49a9216355c6434f73737c29e78c975c8c8bba58aab336a840d72f2d8d55c2"

[P]: R1_stage4_report.md "SHA256 bb1fb0ad58c67570376192b6244e497a1636576f2547b75edff5fb0de9c7350a"

[Q]: freeze_checklist_20261009.md "SHA256 2f6dfdc270406aefdadb1a1bd79d7d1c9ec80db8c7e6411067a0ac750c88d835"

[R]: ../logs/additional_work/reproductions/round63-verified/pc-settings/report.json "SHA256 70f31f34efbf5a454389eac460b6d69c3da670cdef6659c9010ce6a4ffa407e3"

[S]: ../logs/additional_work/HT-17/snapshot-20261004-complete/report.json "SHA256 67386fb2f89f253e7e11f792c33eb8e292ac9c77609881a2a6a0a4c4a7ccc210"

[T]: ../logs/additional_work/R/report-round63-final/report.json "SHA256 6b680ae1cc1891a46835ea6c7fd94c3210f1f5c1a4f2b47d9052b10e950bf872"

[U]: ../logs/additional_work/PC-reader/report-round63-final/report.json "SHA256 e59d5dd8748fb1f3033bae0eb649f141cc77ed0d654a8df9214acdaf0bd9463f"

[V]: ../logs/additional_work/AW-L/report-round63-final/report.json "SHA256 6b598ac22709944667d0ae7816d2ead34cba22a56dda788a4d55e6dd1a7561ca"

[W]: ../logs/r1_round22/ht3e-independent-review-v2.json "SHA256 fac11b2260a5fd554d9b759926127bc0387b4719cd4335db5ecec1d48ae05a34"

[X]: ../logs/additional_work/reproductions/round63-verified/catalog.json "SHA256 de4cfe2edab9437b546360b0c8604ad4033b45c89bddae3bbc100306bad5ba1b"

[Y]: additional_work/HT-17_report.md "SHA256 835f77ccd92c388d6bc44795a2eaf1baf9a019a22c4386a4744aba9338188d92"
