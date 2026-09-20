# H3 distillation sandbox: joint fitting helps; the writable PC extension does not yet

Completed 19 September 2026. Tiny Shakespeare; CPU experiments.

## Main finding

**A smaller student base can be trained to fit the existing H3 CD/PC cap better than either separate distillation or staged task fine-tuning. The additional writable PC interface, in its current finite-step form, did not provide that benefit.** Both statements matter: the experiments support joint base/cap fitting, but do not validate a full error-PC transformer conversion.

I completed **11 variants across three existing H3 cap seeds (33 final continuation fits)**, in addition to development trials, teacher-only distillation, numerical checks, and inference ablations. The final FF sublayer shrinks from 256 to 96 hidden units, reducing the assembled base from **120,576 to 99,936 unique parameters (17.12%)**. H3's nonlinear cap and two genuinely generated CD readers are retained. Their graph is frozen during these distillation experiments.

## Held-out prediction results

Mean bits per byte across cap seeds 7, 19, 37; lower is better. Test has 32,768 positions and the following tail segment has 22,938. Checkpoint selection uses validation only. “Read-only” means the base cannot be changed by the cap during a prediction; its parameters **are** learned jointly during training. PC state inference in the nonlinear cap remains active.

| Variant | Test bpb | Tail bpb | Selected continuation updates (7/19/37) |
|---|---:|---:|---|
| Original teacher + H3 PC cap (continuation allowed) | 2.305708 | 2.384044 | 0 / 0 / 0 |
| Separate distillation, then frozen-student PC cap | 2.306237 | 2.382558 | 0 / 200 / 0 |
| Student task fine-tuning + KD, then PC cap | 2.297331 | 2.378333 | 160 / 200 / 240 |
| Joint distillation, read-only interface, PC training | 2.289393 | 2.373730 | 240 / 240 / 240 |
| Joint distillation, read-only interface, BP training | 2.289320 | 2.374254 | 240 / 240 / 240 |
| Joint distillation, writable interface, BP training | 2.289302 | 2.374268 | 240 / 240 / 240 |
| Joint BP + reader-response teaching | 2.290116 | 2.374700 | 240 / 240 / 240 |
| Joint distillation, writable interface, PC training | 2.306131 | 2.383188 | 160 / 200 / 0 |
| Joint writable PC + zero-port reader auxiliary loss | 2.307077 | 2.383477 | 160 / 200 / 0 |
| Joint writable PC + reader-response teaching | 2.306732 | 2.383161 | 160 / 200 / 0 |
| Joint response PC + diagonal interface metric | 2.305369 | 2.382249 | 0 / 200 / 0 |

The full-teacher continuation baseline selected its initial checkpoint for all three seeds. Thus its scores also reproduce the inherited H3 baseline. Several writable-PC variants likewise selected the initial student/cap checkpoint for one or two seeds: those cases are explicitly retained, not presented as successful new learning.

## How much evidence is there for the joint-fitting gain?

The read-only joint-PC model improved over **separate distillation, staged fine-tuning, and full-teacher H3 in every seed on both held-out segments**. Its gains over the staged control were 0.007938 and 0.004603 bpb. Both training schedules gave each parameter group 240 updates; the staged control had a separate student-selection phase, so the practical comparison does not equalize all optimization and selection details.

The following intervals bootstrap text blocks after averaging paired loss differences over seeds. Positive gain favors joint read-only PC. They are conditional on this reused corpus and the shared teacher/reader graph, not across-corpus confidence intervals.

| Reference | Segment | Gain | 95% interval, 256-byte blocks | 95% interval, 1,024-byte blocks |
|---|---|---:|---|---|
| Separate distillation, then frozen-student PC cap | test | 0.016844 | [0.014538, 0.019238] | [0.013580, 0.020313] |
| Separate distillation, then frozen-student PC cap | tail | 0.008828 | [0.006641, 0.011075] | [0.006158, 0.011502] |
| Student task fine-tuning + KD, then PC cap | test | 0.007938 | [0.006767, 0.009145] | [0.006521, 0.009365] |
| Student task fine-tuning + KD, then PC cap | tail | 0.004603 | [0.003586, 0.005625] | [0.003567, 0.005662] |
| Original teacher + H3 PC cap (continuation allowed) | test | 0.016315 | [0.013864, 0.018851] | [0.013246, 0.019567] |
| Original teacher + H3 PC cap (continuation allowed) | tail | 0.010314 | [0.007985, 0.012627] | [0.007504, 0.013062] |

Read-only PC and BP are close: neither is a clear general winner here. PC is slightly better on the tail, while their test means are nearly identical. This supports the practical feasibility of the PC-cap training variant at this scale; it does not establish superiority of PC learning.

An especially informative control is the student's standalone accuracy:

| Training | Student alone, test | Student + cap, test | Student alone, tail | Student + cap, tail |
|---|---:|---:|---:|---:|
| Separate distillation, then frozen-student PC cap | 2.899490 | 2.306237 | 2.968136 | 2.382558 |
| Student task fine-tuning + KD, then PC cap | 2.880124 | 2.297331 | 2.959232 | 2.378333 |
| Joint distillation, read-only interface, PC training | 2.889415 | 2.289393 | 2.966952 | 2.373730 |

Staged fine-tuning makes the student itself more accurate, yet joint fitting makes the **combined system** more accurate. That is the useful positive evidence for fitting the base to the cap. The generated CD readers still receive about 30.8% of average test mixture weight. The direct student reader receives about 3.2%; student-backed copy readers and the cap's hidden features provide additional routes for student influence.

The original full-width base was not jointly fine-tuned in this experiment. Consequently the results show that compression is **compatible with** a joint-fitting gain, not that compression itself causes the gain.

## What failed or remained unproven?

1. **Writable PC lost the joint-fitting benefit.** Its test/tail means were 2.306131/2.383188, versus 2.289393/2.373730 for matched read-only PC. The writable-PC disadvantage occurred in every seed on both segments. Against separate distillation, its mean gain was essentially zero on test and slightly negative on tail, with mixed signs across seeds.

2. **Writes did not help BP either.** Training with a writable BP interface was essentially tied with read-only BP. Disabling writes in the already-trained models marginally improved mean held-out predictions. Thus the good BP joint-fitting result is not evidence that feedback corrections matter.

3. **Reader-response teaching did not give a net predictive gain.** In BP it slightly worsened both mean prediction scores. In PC it worsened test and was essentially tied on tail relative to no response loss. It did beat the zero-port reader-auxiliary control by approximately 0.0003 bpb, so the response mechanism has a small signal relative to that particular control; both auxiliary objectives nevertheless failed to beat ordinary joint training.

4. **The diagonal metric did not rescue the architecture.** Its selected models remained far behind read-only joint fitting; two seeds selected step zero. Its apparent mean improvement over unpreconditioned response PC is not a consistent new-learning gain across seeds.

Inference write ablations (positive means enabling the writes helps):

| Variant | Test write gain | Tail write gain | Mean test correction norm |
|---|---:|---:|---:|
| Joint distillation, writable interface, BP training | -0.0000375 | -0.0001038 | 0.001964 |
| Joint BP + reader-response teaching | -0.0000356 | -0.0001032 | 0.001957 |
| Joint distillation, writable interface, PC training | -0.0000199 | -0.0000658 | 0.001994 |
| Joint writable PC + reader-response teaching | -0.0000190 | -0.0000637 | 0.001995 |
| Joint response PC + diagonal interface metric | -0.0001004 | -0.0001782 | 0.003274 |

The prediction-time effect of writes is around 10^-5–10^-4 bpb, much smaller than the approximately 10^-2 bpb training gap between writable and read-only PC. This locates most of that gap in the learned models/training procedure, rather than the immediate effect of applying the final correction. It does not by itself identify the exact optimization failure.

## The response task was learned, but did not transfer

For response-supervised BP, the learned proposal reduces KL to its artificial reader/teacher teaching target on held-out prefixes:

| Segment | KL without proposal (bits) | KL with proposal (bits) | Proposal correction norm | Natural inference correction norm |
|---|---:|---:|---:|---:|
| test | 0.033902 | 0.028183 | 0.068667 | 0.001957 |
| tail | 0.035102 | 0.029288 | 0.068621 | 0.001951 |

So the issue is not simply that the student cannot learn to respond. The proposal uses a full reader-versus-teacher residual vector, whereas normal free inference receives only the cap's much coarser current reader summaries and recent evidence, and starts its correction at zero. The training-only proposer is then discarded. The intended response and deployed inference therefore differ in available information, initialization, and correction magnitude.

There is also a structural limitation in the surrogate objective. In the idealization of exact teacher imitation and **fixed companion reader distributions**, if a corrected student exactly matches $0.9T+0.1q_j$, then a mixture containing that student and the non-student readers can be rewritten as

$$w_0(0.9T+0.1q_j)+\sum_k w_kq_k=0.9w_0T+(w_j+0.1w_0)q_j+\sum_{k\ne j}w_kq_k.$$

That teaching target is already inside the convex hull of the teacher and that CD reader. With fixed companion readers, perfectly imitating it does not expand the mixture's output possibilities. In the actual implementation, student-backed copy readers also change, so this argument is **not** an expressivity theorem for the complete architecture. Nor does it prove that all trained student outputs remain in the hull or that hidden-feature learning cannot help. It explains why a good response-surrogate score alone is weak evidence for an additional predictive capability.

## Numerical and runtime findings

All 11 test methods passed. A strengthened raw-prefix check also confirms that the teacher-free full output distribution gives the same actual-target likelihood as the cached scoring path. Independent raw-data regeneration exactly matched inherited features and reader likelihoods on 64 development prefixes. Model/optimizer continuation was tested for both PC and BP.

A separate double-precision audit used one development prefix and a genuinely converged reference state (state-gradient norm below 4e-14; minimum Hessian eigenvalue about 0.01935). It compared the finite PC task gradient with the implicit equilibrium derivative and finite-step BP:

| Settling steps | Cosine to equilibrium gradient | Relative error to equilibrium | Cosine to same-horizon BP |
|---:|---:|---:|---:|
| 32 | 0.267 | 0.997 | 0.850 |
| 128 | 0.451 | 0.985 | 0.895 |
| 512 | 0.954 | 0.468 | 0.567 |

The manual energy derivatives are correct, but 32-step PC is not an accurate equilibrium-gradient calculation in this checked example. Finite-step credit assignment is therefore a plausible contributor to the writable-PC failure. One prefix is a diagnostic, not a population estimate or proof of the failure's cause.

Longer development inference did not reveal a large prediction gain to amortize: for joint writable PC, 32/64/128 steps gave 2.356618/2.356355/2.356601 bpb. Response-PC behaved similarly. I therefore did not add a long-settling-to-short-settling distillation stage.

The teacher-only warmup reduced development teacher KL from 0.29727 to 0.001447 bits. Its held-out KL was 0.001464/0.001511 bits. This confirms close output imitation for the compressed module on this corpus. It is not a test of forgetting or broad capability retention.

The main three-process continuation launch took about 711 seconds after resuming the initial serial work, with two Torch threads per process. That excludes cache construction, development, some earlier training, evaluation, and reporting. Raw-prefix inference for a batch of 16 took approximately 67–74 ms in a small shared-CPU check. There was **no demonstrated end-to-end speedup** from the parameter reduction. The wrapper and count readers are unoptimized; read-only paths also recompute quantities that a production implementation could cache.

## What I would carry forward

- Use **teacher-anchored joint distillation with the nonlinear CD/PC cap and a read-only base interface** as the established small-scale baseline. It retains the generated CD patterns and PC cap dynamics. BP training is a close practical control.

- Before scaling the writable variant, calibrate its finite-step PC parameter gradients against finite-step BP on a representative batch of prefixes, separately for student and cap parameter groups. Test adaptive settling or broader state preconditioning; the current diagonal correction-only metric was insufficient.

- Make the same reader-to-correction signal available in training and inference. One candidate is a small proposal head on the existing cap, driven by projected **reader-versus-student** residuals, with a learned correction prior or initialization. This avoids requiring teacher outputs at deployment and avoids discarding the translator used in response training.

- Teach useful compositions of CD distinctions, rather than only a convex blend that the existing mixture can already express. A candidate target uses learned, regularized log-probability increments along a dependency tower: $\log p^*=\log p_0+\alpha(\log q_{\rm parent}-\log p_0)+\beta(\log q_{\rm child}-\log q_{\rm parent})-\log Z$. Its utility must be selected on actual next-byte prediction, since correlated readers can otherwise amplify errors. This is a proposed next experiment, **not a result obtained here**.

These results do not test new CD reader discovery during distillation, search warmup, whole-transformer error-PC conversion, continual learning, or frontier-scale training. They support a concrete partial co-distillation method and expose limitations of the first writable extension.

## Reproducibility

The companion ZIP includes executable code, the corpus and original teacher, reader tables, parent cap states, student warmup, all development and final model/optimizer checkpoints, per-target test/tail losses, checkpoint hashes, logs, and analysis scripts. Large regenerable caches are excluded. `README.md` gives commands; `PROTOCOL.md` records the pre-evaluation design; `results/main/analysis.json` contains all paired comparisons, per-seed scores, and both block sizes.

The methods below give the exact architecture and objective.

---

# Method and interpretation of this sandbox experiment

## The question

Can a small student transformer module be trained to work especially well with H3's CD/PC cap, rather than first copying a teacher and only later attaching the cap? A second question is whether the student benefits from an internal interface through which causal PC inference can adjust its computation. A third question is whether explicitly teaching responses to CD readers makes that interface useful.

These are distinct claims. Better joint prediction alone does not show that the writable interface matters, that reader-response training adds value, or that PC beats BP. The controls and write-disable diagnostics separate those claims.

## What is retained and what changes

The inherited teacher is a two-block, width-64, four-head, 64-byte-context transformer with 120,576 unique parameters and tied embedding/readout weights. Only its final feed-forward sublayer is compressed: hidden width 256 becomes 96. The preceding computation, including attention, stays frozen. The final sublayer's two linear maps, its input layer normalization, and the output normalization are trainable. This gives an assembled student base with **99,936 unique parameters**, a 17.12% reduction. The final FF sublayer itself loses 62.5% of its hidden units; that is not a 62.5% reduction of the entire base.

The nonlinear H3 cap has hidden widths 96 and 64 and 15 reliability outputs. Its 19,183 parameters are retained. Thirteen inherited readers are joined by the two actual generated H3 readers: word-prefix and word-prefix-plus-previous-word, with learned count distributions and a parent/backoff relationship. Thus the experiment uses previously learned CD programs, not just a selection among the original fixed readers. Those programs and their tables are held fixed during distillation. There is no new reader birth or search-guide update in these fits. Neural-module compression by distillation and CD's structural compression objective are different mechanisms; the latter is held fixed here.

The assembled student-plus-cap has 119,119 learned parameters, compared with 139,759 for the teacher-plus-cap, excluding a fixed 1,024-entry correction matrix. Count-table storage is unchanged and dominates this tiny neural model's storage. A 21,584-parameter response proposer is used only during training in response-supervised arms and is unnecessary at deployment. These counts are not a claim of comparable end-to-end latency savings.

## In elementary terms

1. Read the preceding 64 bytes through the retained transformer computation.
2. Run the smaller student module. It proposes a next-byte distribution and supplies features for the cap.
3. Ask the CD readers for their predictions, and check how well all readers explained the last 16 already-observed bytes.
4. Let the cap revise its internal states and reader weights to reconcile that recent evidence with its learned prior. Writable variants may also make a small change to the student's internal input.
5. Mix the reader distributions using the settled weights. The actual next byte is used only for training or scoring after the prediction.

All confidence/entropy/agreement summaries are recomputed from the uncorrected student and current count-reader distributions, then held fixed within the current prediction's settling. The student's current hidden features remain writable. This distinction permits teacher-free inference while keeping the small PC energy tractable.

## Prediction and state energy

Let $u(x)$ be the frozen trunk state and $g_\theta$ the compressed final module. With a fixed rank-16 matrix $U$, define

$$h_\theta(x,e)=g_\theta(u(x)+Ue),\qquad p_\theta(\cdot\mid x,e)=\operatorname{smooth}(\operatorname{softmax}(Wh_\theta(x,e))).$$

The columns of $U$ are orthogonal and have length 0.1. Smoothing is $(1-1/256)p+(1/256)/256$, as in H3. The student is initially fit to the teacher by 800 batches of teacher-to-student KL, using a shared 65,536-position training pool.

The free inference state is $s=(e,a,b,z)$, where $a\in\mathbb R^{96}$, $b\in\mathbb R^{64}$, and $z\in\mathbb R^{15}$. Write $w=\operatorname{softmax}(z)$ and $f_1,f_2,f_3$ for the cap's two tanh maps and final linear map. Its free energy is

$$E_0(s;x)=\frac12\left[\rho\|e\|^2+\|a-f_1(h_\theta(x,e),r_\theta(x))\|^2+\|b-f_2(a)\|^2+\|z-f_3(b)\|^2\right]-\frac{\eta}{16}\sum_{i=1}^{16}\log\left(\sum_j w_j q_{ij}\right).$$

Here $r_\theta(x)$ contains the student-derived reader summaries, and $q_{ij}$ is reader $j$'s probability for observed prefix byte $i$, evaluated using only that byte's preceding context. The student-dependent prefix probabilities use the uncorrected student. The constants are $\rho=0.1$ and $\eta=2$.

The next-byte prediction is

$$P_{\theta,\phi}(y\mid x,s)=\sum_j w_jq_j(y\mid x,e).$$

The student and base-backed copy readers change with $e$; the other reader distributions remain fixed. Free inference takes 32 simultaneous gradient steps of size 0.15, starting at zero correction and the feed-forward cap states. Read-only arms keep $e=0$.

The diagonal-metric arm divides the correction-coordinate gradient by

$$D_{kk}=\rho+\sum_a\left(\frac{\partial f_{1,a}}{\partial e_k}\right)^2,$$

evaluated at initialization and held fixed during settling. This is a positive diagonal Gauss–Newton approximation for that interface, not a learned full error metric or a full transformation of transformer attention into predictive coding.

## Learning objectives and controls

Let $T(\cdot\mid x)$ be the frozen teacher distribution and $\ell=-\log P(y\mid x,s)$. All joint arms add the ordinary teacher anchor

$$L_{\rm KD}=D_{\rm KL}(T\|p_\theta(\cdot\mid x,0)).$$

Response supervision chooses one of the two accepted CD readers $q_j$, constructs a soft teaching target

$$t_j=0.9T+0.1q_j,$$

and learns a proposal $\hat e_j=0.5\tanh A_\psi(h_\theta(x,0),\operatorname{clip}(\log q_j-\log T)/8)$. Its loss is

$$L_{\rm response}=D_{\rm KL}(t_j\|p_\theta(\cdot\mid x,\hat e_j)).$$

The overall joint training objective adds $L_{\rm KD}+0.3L_{\rm response}$ to the task-learning signal. Teacher targets and the proposer are training aids. Neither is needed for free inference. The **zero-port reader-auxiliary control** uses the same $t_j$ but forces $\hat e_j=0$, distinguishing interface-response teaching from ordinary reader-guided soft-label training.

BP differentiates the 32-step forward trajectory. PC settles positive and negative nudged states under $E_\beta=E_0+\beta\ell$, with $\beta=\pm0.05$, using 32 additional steps from the same free state. It estimates the task parameter gradient by

$$\widehat g=\frac{\partial_{\theta,\phi}E_{+\beta}(s_+)-\partial_{\theta,\phi}E_{-\beta}(s_-)}{2\beta}.$$

These are fixed-state parameter partials: the PC implementation does not backpropagate through the settling trajectory. It **does** use autograd for the student module and parameter partials, including the dependence of prefix probabilities and reader summaries on student parameters. This is a hybrid implementation, not an all-local training rule for every transformer layer. At finite settling time the displayed gradient is an approximation; numerical diagnostics quantify that limitation.

The staged control first trains the student alone with next-byte CE plus teacher KL for 240 updates, selecting by standalone validation CE, then freezes it and trains the cap for 240 updates. Each parameter group receives the same update count as in a joint arm. The two-stage schedule and its additional selection opportunity remain differences, so this is a strong practical control rather than an exact causal factorial experiment.

## Protocol and checks

The corpus split is chronological 90/5/5. Reader count tables use the first 700,000 training bytes. The inherited fit pool has 65,536 later training positions. Development uses 4,096 positions in the first validation half; checkpoint selection uses 4,096 in the second half. Each continuation fit draws 240 batches of 128 positions: **30,720 sampled examples with replacement**, not a fresh full pass over all 65,536 pool positions. The inherited H3 caps already received their earlier training.

All variants start from matched inherited cap checkpoints, and compressed variants share the same teacher-only student warm start. Seeds 7, 19, and 37 vary cap history and continuation minibatches; they do not give independent pretrained transformers, reader graphs, or student-distillation initializations. The final recipe is selected before new test evaluation. Step zero is an eligible checkpoint, so a method is not forced to keep harmful continuation updates. Hashes lock models before scoring 32,768 test bytes and the following 22,938 tail bytes.

Eleven tests cover exact manual state derivatives, the student Jacobian, positive diagonal metric, target-free inference, causal trunk states, vectorized copy counts, teacher/full-width recovery, old-H3 recovery, exact optimizer continuation for PC and BP, a small energy-descent check, response gradients, independence from teacher summaries, and raw-prefix teacher-free prediction matching the cached experiment. Some test methods check several related properties. Independent regeneration reproduces inherited reader features and likelihoods exactly on 64 checked development prefixes.

Exploratory development included a stronger port (scale 0.5, precision 0.02). It produced much larger unpreconditioned corrections but worse validation predictions. The initial development implementation retained teacher confidence summaries; it was replaced with student-derived summaries before final comparisons. Both exploratory versions and source snapshots are preserved. The final deployment path contains no teacher final FF sublayer.

Paired intervals resample non-overlapping text blocks, with block lengths 256 and 1,024, after averaging each position's loss difference over the three seeds. They describe uncertainty conditional on this reused text and shared pretrained components. They are not independent-corpus generalization intervals, and no multiplicity correction is claimed. The corpus has already informed previous H3 work, so this study remains exploratory even though the new checkpoint choices precede its held-out evaluation.
