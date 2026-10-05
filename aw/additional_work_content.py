"""Authored FIN-1 reading guide; tables come unchanged from the named reports."""

SOURCES = {
    "A": "docs/additional_work/PC-v0_report.md",
    "B": "docs/additional_work/PC-controls_report.md",
    "C": "docs/additional_work/PC-matched-control_report.md",
    "D": "docs/additional_work/PC-v1_report.md",
    "E": "logs/additional_work/reproductions/round63-verified/documents/PC-settings_report.md",
    "F": "docs/additional_work/AW-B_report.md",
    "G": "docs/additional_work/PC-reader_report.md",
    "H": "docs/additional_work/R_report.md",
    "I": "docs/additional_work/AW-L_report.md",
    "J": "../assets/presentation-materials/reproductions/round63-verified/ht13/table.md",
    "K": "logs/additional_work/round48/HT-15b-270/tail_spread.md",
    "L": "logs/additional_work/HT-17/snapshot-20261004-complete/report.md",
    "M": "logs/r1_round18/ht3d-pilot-final-aliases.md",
    "N": "docs/decisions.md",
    "O": "docs/REPRODUCE_additional_work.md",
    "P": "docs/R1_stage4_report.md",
    "Q": "docs/freeze_checklist_20261009.md",
    "R": "logs/additional_work/reproductions/round63-verified/pc-settings/report.json",
    "S": "logs/additional_work/HT-17/snapshot-20261004-complete/report.json",
    "T": "logs/additional_work/R/report-round63-final/report.json",
    "U": "logs/additional_work/PC-reader/report-round63-final/report.json",
    "V": "logs/additional_work/AW-L/report-round63-final/report.json",
    "W": "logs/r1_round22/ht3e-independent-review-v2.json",
    "X": "logs/additional_work/reproductions/round63-verified/catalog.json",
    "Y": "docs/additional_work/HT-17_report.md",
}

# (title, source, table header prefixes, framing, cost groups). A prefix must
# select exactly one table, except the explicitly indexed checkpoint-300 table.
SECTIONS = [
    (
        "PC-v0: does corrected error settling improve acquisition?", "A",
        [("| Dataset | metric |", 0), ("| Dataset | Arm | Cells |", 0)],
        """**Design and exposure.** DEC-074/074b authorized corrected SE-E versus adjoint SE-A with fresh memories on the original **ePC 50M frozen base and v0 C1 live cap**, not the GPT-2-small main-study model. Sixty cells cross two datasets, three previously exposed S5 subject realizations, five orders and two arms. zsRE reaches 1,000 edits; CounterFact reaches 300. Eight error iterations at rate .1 use the corrected quadratic error prior. Credit computation still uses autodifferentiation; this is not a demonstration of local, backpropagation-free learning. [A] [N]

**Reading and limits.** zsRE own-prompt retention improves by .0203333, while paraphrase retention changes by −.0028 with mixed realization signs. CounterFact saturates own-prompt retention with zero paraphrase retention in both arms. The harm readout uses only 32 windows / 4,064 positions, and cannot be directly pooled with the full 245,237-position assay below. Positive-loss expected shortfall and the difference between two arms' shortfalls are distinct from the shortfall of paired loss differences. [A]""",
        ["PC-v0 default"],
    ),
    (
        "PC-v0 control 1: settling depth", "B", [("| Dataset | Depth | Arm |", 0)],
        """**Design and exposure.** DEC-075 adds one- and 32-step settling to the eight-step reference, using order 100 only, the same three exposed realizations and both datasets: twelve cells per depth. The eight-step rows reuse the default study and are charged there. [B] [N]

**Reading and limits.** One-step normalized credit matches adjoint algebraically; tiny saved harm-vector differences are floating-point effects. More settling raises zsRE own-prompt retention but does not consistently improve paraphrase retention or harm, and costs more. CounterFact's saturation limits discrimination. Three realizations and one order do not establish general PC superiority. [B]""",
        ["PC-v0 depth 1", "PC-v0 depth 32"],
    ),
    (
        "PC-v0 control 2: random credit direction", "B", [("| Arm | Status | Items |", 0)],
        """**Design and exposure.** DEC-075/079 replace the true credit's direction with a random direction of equal norm, paying for the true credit first. Of six planned pairs, only the first exposed zsRE r0/order-100 pair ran. Adjoint completed 1,000 items; random credit stopped under its unchanged resource allowance at 993. Ten cells were never started. [B] [N]

**Reading and limits.** Three random-arm immediate answers succeeded. The table's immediate-ES denominators differ; on the common first 993 items, adjoint is .997986 versus .003021 for random credit. Missing final retention and separate full-vector control harm remain missing. This supports informative credit in this implementation, not a general impossibility of random search. The native report corrects DEC-079's historical unstarted-cell count. [B]""",
        ["PC-v0 random"],
    ),
    (
        "PC-v0 control 3: adjoint offered the PC acquisition budget", "C",
        [("| Dataset | Realization | ES |", 0), ("| Dataset | Realization | Offered ops |", 0)],
        """**Design and exposure.** DEC-075 and the lead's clarification fund additional acquisition updates for adjoint. Twelve cells / six pairs use the same exposed populations and order 100. The first table is SE-AM minus ordinary SE-A. [B] [C] [N]

**Reading and limits.** The control uses only about 53–58% of the offered operations because threshold stopping and rollback remain active. It does not recover the eight-step own-prompt gain, but it is **not an equal-realized-compute comparison**. Operations are not FLOPs; differences in prefix traversal and stopping leave direction versus effective compute unresolved. Separate full-vector control harm curves were not supplied. [B] [C]""",
        ["PC-v0 offered-budget"],
    ),
    (
        "Fixed-v5 reader: change acquisition credit only", "D",
        [("| Dataset | Arm | ES |", 1), ("| Dataset | Arm | Cells |", 0)],
        """**Design and exposure.** DEC-074/074b hold the selected BP-trained v5 reader and frozen GPT-2-small base fixed, comparing SE-A and corrected SE-E acquisition into fresh memories. Four cells use both datasets, exposed r0/order 100, through 300 edits. The efficacy table is checkpoint 300. Full ordinary-text harm uses 1,931 windows / 245,237 positions. [D] [N]

**Reading and limits.** Paraphrase differences are zero on zsRE and −.003333 on CounterFact; ES99+ falls on zsRE and rises on CounterFact. This is one exposed realization, not an equivalence test. The original harm invocation finished its numerical readouts but failed while formatting its final table; the failed receipt remains failed, and saved vectors were independently verified. [D]""",
        ["Fixed-v5 default"],
    ),
    (
        "Fixed-v5 settings: deeper settling and two error rates", "E",
        [("| Setting | Dataset | Arm |", 0)],
        """**Design and exposure.** DEC-077 adds 32 iterations at rate .1, and rates .05/.2 at eight iterations. Each setting has its own development profile, four exposed r0/order-100 cells through 300 edits and full-vector harm. The table is copied from the completed Round-63 reproduction; all setting-specific harm statistics and costs remain in its companion report [R]. [E] [N]

**Reading and limits.** None supplies an independent subject replication or demonstrates a broad advantage over adjoint. The default/settings use repeated subjects and cannot be counted as new independent realizations. Three failed initial harm launches have logs but no separate preserved duration receipt; the cost total explicitly leaves that gap open. [E] [R]""",
        ["Fixed-v5 settings"],
    ),
    (
        "AW-B: a bounded query-time correction", "F",
        [("| Memory | Setting | ΔES |", 0), ("| Setting | Every coordinate passes |", 0)],
        """**Design and exposure.** DEC-073/076/076a prescribe development calibration on the actual full-endpoint saved-memory populations, eligibility on both datasets, then maximize the smaller maximum-harm reduction (ES99 reduction breaks ties). The selected mixture uses ρ=exp(−1). Evaluation uses ten already exposed r0 memories: two datasets × five orders at 300 edits. No eligible shrinkage or stricter-gate comparator was selected. [F] [N]

**Reading and limits.** All ten evaluation coordinates pass the registered comparison rule. Mixing p_mix=ρ p_base+(1−ρ)p_cap proves ΔNLL≤−lnρ=1 nat **for a token at the identical prefix**. Severity drops substantially, frequency changes little, and CounterFact loses some paraphrase retention. This is not a sequence-level or KL bound, nor a recommended cap configuration (DEC-078). It is a known ceiling on the observable, not a demonstrated change in distribution class (DEC-081a). Group frequency/severity results are also copied in HT-17 below. [F] [L] [N]""",
        ["AW-B calibration", "AW-B evaluation"],
    ),
    (
        "PC-trained reader: three paired training seeds", "G",
        [("| Dataset | Seed | BP RET-ES |", 0), ("| Paired seed |", 0)],
        """**Design and exposure.** DEC-077 trains the v5 reader recipe for 300 steps with corrected ePC versus BP, three paired seeds each. All six trainings and twelve evaluations are complete. Evaluation remains the same exposed r0/order-100 subjects, both datasets at 300 edits, with adjoint acquisition for both reader families. Seeds are training replications, not fresh subject draws. [G] [N]

**Reading and limits.** CounterFact ePC loses paraphrase retention in all three pairs; zsRE differences are mixed. CounterFact harm/firing signs reverse across seeds; a universal safer-reader claim is unsupported. The training-time ratios are about 96–102× BP under the installed JAX implementation. This compares the implemented training procedures, not all possible PC methods. Six BP full-read evaluation controls are later reused by AW-L and charged only here. [G]""",
        ["PC-reader"],
    ),
    (
        "Option R: a fourth subject realization", "H",
        [("| Dataset | Edits | Metric | Paired orders", 0)],
        """**Design and exposure.** DEC-073 reserves fresh subjects; DEC-077 launches realization 3, both datasets, five orders, 1,000 edits. DEC-080 defers the v0 class after its first cell hits a ceiling: twenty learned/random cells complete, one v0 cell incomplete and nine v0 cells unrun. Realization 3 was untouched at allocation; the four-realization sensitivity combines it with the already observed r0–2. [H] [N]

**Reading and limits.** Learned-minus-random paraphrase retention stays positive in the four-realization display. Five orders are first averaged within each realization; they are not twenty independent replicates. The t(3) intervals are unadjusted small-cluster sensitivity displays, not reissued registered classifier labels or a new familywise coverage claim. Missing v0 results remain unavailable. Its scalar drift path and unchanged ceiling explain the stopped cell; no post-outcome repair was substituted. [H]""",
        ["Option R"],
    ),
    (
        "Upper-layer 2×2: reading upper features and writing only at the last tap", "I",
        [("| Dataset | Seed | Read | Last−all", 0)],
        """**Design and exposure.** DEC-073/077 cross all versus upper reader features with all versus last-only write taps, both datasets and three paired BP seeds, at exposed r0/order 100 through 300 edits. All twenty-four cells are complete; six full-read/full-write controls come from PC-reader. Reader training uses the full-write recipe; last-only writing is an evaluation intervention, not a separately trained last-write model. [I] [N]

**Reading and limits.** Last-only writing raises mean ordinary-text loss by roughly 2.64–4.37× in all twelve paired blocks while changing paraphrase retention little. Upper features do not establish that lower features are noise; the upper-trained CounterFact reader loses paraphrase retention in every seed, and one seed has notably poorer acquisition. Architecture, training and gating interactions constrain interpretation. The table separates write effects within each read/seed setting. [I]""",
        ["AW-L new work"],
    ),
    (
        "HT-13: pooled frequency, severity and concentration", "J",
        [("| condition | dataset |", 0)],
        """**Question, design and exposure.** The CPU reporting lanes following the DEC-074b halt describe all 270 receipted Stage-4 cells, using their saved full-position vectors against each model's own cap-off base. No new GPU experiment or subject is introduced. The native table below is the verified Round-63 refresh. [J] [P]

**Reading and limits.** Rare large losses can coexist with small averages. ES99+ is a fractional worst-1% average with zero mass retained, not the 99th percentile and not a positive-only conditional mean. The same positions are repeated across cells: pooled cell-position counts are not independent sample sizes. For S1, own cap-off means the continued base, not the original GPT-2. Concentration does not establish an asymptotic heavy-tail law. [J] [K]""", [],
    ),
    (
        "HT-15: cell-level and realization spread", "K",
        [("| Condition | Dataset | Cells / 15 |", 0)],
        """**Question, design and exposure.** The post-halt HT-15b reporting lane asks how much the pooled result varies across the same 270 completed cells, with three realizations and five dependent orders per group. The table retains every observed condition/dataset, including S1_literal zsRE's fifteen completed cells. [K] [P]

**Reading and limits.** Compute the cell statistic first, then average five orders within each realization. Realization ranges are descriptive, not confidence intervals; pooled ES99 and mean cell ES99 are different estimands. MQuAKE ends at 300 edits; its rows do not imply 1,000-edit evidence. Unrun conditions are absent evidence, not zero harm. These lanes consume saved results and have zero additional GPU cost. [K]""", [],
    ),
    (
        "HT-17: saved-vector finite-range tail analysis", "L",
        [("| Study | Dataset | Condition | Cells |", 0)],
        """**Question, design and exposure.** DEC-081a authorizes CPU-only analysis separating the probability of Δ>.01 from its conditional severity and from gate firing, then comparing generalized-Pareto excess fits with exponential fits on held-out windows. The final snapshot has 303 cells: 225 Stage-4 zsRE/CounterFact, 30 AW-B, twelve PC-reader and 36 legacy pilot. AW-L and Option R are outside this fit inventory. The source's old generic sentence about a pending reader comparison does not override its zero-pending, twelve-reader-cell inventory or the final reader report [G]. [L] [S] [N]

**Reading and limits.** Fits concern observed finite ranges, not complexity classes, accessible-state growth W(N), infinite variance or measured temperature. Fitted learned-reader shapes show little held-out advantage over exponential; invalid/sparse fits stay invalid, including likelihood endpoints and shapes outside the declared entropy domain. This does not weaken AW-B's analytic ceiling. Joint window resampling conditions on the fixed cells; it does not measure new-subject uncertainty. Full 1,931-window and legacy 32-window populations are never merged. Historical pilot MQuAKE retention and drift populations differ. Complete fits, diagnostics and intervals remain in [L]; the accessible interpretation is [Y]. [N]""", [],
    ),
    (
        "Legacy κ pilot: a bounded surprisal loss", "M",
        [("| Arm | RET-GS macro |", 0)],
        """**Question, design and exposure.** DEC-054 authorized κ=.2/.5 and clip-2 against reused ordinary v5-family readers, three seeds each, on the older development populations. All 36 endpoint rows are complete. This September-16 experiment predates the halt; it is included for the scientific narrative, not charged to the new portfolio. For surprisal ℓ, the implemented loss is (1−exp(−κℓ))/κ. [M] [N] [W]

**Reading and limits.** Both κ arms fail the prespecified retention floor and neither tail reduction exceeds the ordinary seed-spread criterion. The clipped control shares κ=.5's ceiling, not κ=.2's; it is not evidence for a κ-specific advantage. ES95 here is different from the ES99 measure above. These are preliminary hints, not the coupled free energy (no coupled expectation or changed inference distribution), not a coupled Markov blanket, and not a test of a shared κ for porosity and interference. Its null does not test the unimplemented coupled objective (DEC-081a). Nine new trainings and endpoint evaluations have partial measured receipts, but historical drift assays lack enclosing durations: a complete pilot GPU total is unavailable, not zero. The receipt catalog and reproduction guide retain the known components. [M] [N] [O] [X]""", [],
    ),
]

INTRO = """# Supplemental programme: predictive coding, bounded correction and rare harm

**Completed results through October 4, 2026; assembled October 5 (FIN-1).** This is the consolidated entry point after the Stage-4 halt, with the earlier κ pilot retained as context. Lettered citations link the exact reports; the accompanying registry records their SHA-256 hashes. Headline tables are copied verbatim, without rescoring, new fits or reclassification.

## Main finding and scope

The programme supports selective correction with measurable trade-offs. Corrected predictive-coding acquisition changes some outcomes but establishes no broad advantage over adjoint credit. Training the reader with the installed ePC procedure is far more expensive and loses CounterFact paraphrase retention. A query-time mixture supplies a proven one-nat ceiling at an identical prefix; it reduces severe observed harm without resolving every fidelity or retention limitation. Upper-layer restriction is not a demonstrated improvement. The additional subject realization reinforces learned-versus-random paraphrase retention, while the stable-v0 extension remains incomplete. [A] [D] [F] [G] [H] [I]

For a reader new to the project: a **cap** is a small correction/memory mechanism attached to a frozen language model. Acquisition writes requested facts into memory; readout decides when to apply them. **ES** is immediate edit success, **RET-ES** retention on original edit prompts, **RET-GS** retention on paraphrases, and **LS** locality preservation. Higher task scores are usually desirable. ΔNLL is cap loss minus its own cap-off loss at the same text prefix; positive values mean harm, measured in nats. A small average does not preclude rare large changes. ES99+ averages the worst 1% of positive-part losses, including zero mass in its denominator. [P] [L]

The main Stage-4 report [P] covers 270 completed cells and remains separate. Passing data-integrity checks does not imply passing its mean-KL ≤.001 benchmark: all 45 main learned-reader cells fail that benchmark. The supplements change different parts of the system and use different populations; their cells must not be pooled as independent confirmations. Most are post hoc studies on exposed subjects. Option R's new r3 subject draw and the reader's three training seeds provide different kinds of replication. [P] [G] [H]
"""

CLOSING = """## What the programme supports, and what it does not

**Predictive coding:** corrected error settling has now been tested in acquisition and in reader training. Its effects depend on substrate, endpoint and compute; no general superiority or biological locality follows. The original ePC-50M/v0 experiment must remain separate from GPT-2-small/v5. [A] [D] [G]

**Heavy-tailed distributions:** the data demonstrate rare, concentrated harm and finite-range tail behavior. They do not establish an asymptotic heavy-tail class, infinite variance, an entropy measurement, or the growth of accessible states. The mixture ceiling is an algebraic bound on the measured token observable, not a fitted class transition. The κ loss pilot tests a bounded deformation of surprisal, not the untested coupled-entropy/free-energy proposal. This follows the approved DEC-081a wording. [L] [M] [N]

**Active inference in the Extremes:** selective correction and its costs are a useful experimental substrate for an active-inference programme. Autonomous expected-free-energy policy selection, an informational coupled-free-energy objective, and a validated κ-porous/Markov-blanket interpretation remain proposed work. No equation has been selected as that future training objective. DEC-082 retains those questions for post-conference collaboration; the optional extra κ readout and 3,000-edit scaling study are closed without execution. [N]

**Generalization:** GPT-2-small (124M parameters), English benchmark editing, limited subject draws, exposed evaluations and dependent text positions do not establish behavior in larger or deployed systems. The original v0 PC substrate is smaller still. Training seeds, stream orders, windows and subject realizations are different units of variation. Better prompt retention is not equivalent to factual correctness, safety or overall model fidelity. [P] [G] [L]

## Remaining work and schedule

DEC-083 closes the GPU portfolio: the last GPU step finished October 4 at 01:17. No new fits are planned. The October-6 freeze dry run, final source/audit refresh, lead's October-9 17:00 EDT freeze, and preparation for the October-15 presentation remain. The freeze checklist [Q] assigns the lead's signature; this report is not that signature. Colleague-talk revisions await charlie's rehearsal feedback. [N] [Q]
"""
