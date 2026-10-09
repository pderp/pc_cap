"""Render the entropy/tail analysis as the requested support document and figures."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
DATASETS = ("zsre", "counterfact", "mquake")
NAMES = {"zsre": "zsRE", "counterfact": "CounterFact", "mquake": "MQuAKE"}
CONDITIONS = ("R1_learned_ff", "v0_stable", "R1_nonlearned")
LABELS = dict(R1_learned_ff="Learned v5", v0_stable="Stable v0", R1_nonlearned="Random reader")


def f(x, digits=5):
    return "undefined" if x is None else f"{x:.{digits}g}"


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
                     + ["| " + " | ".join(str(v) for v in row) + " |" for row in rows])


def shape_row(cells, field, threshold="0.01"):
    tails = [c[field][threshold] for c in cells]
    shapes = [r["fit"]["shape"] for r in tails if r["fit"]["status"] == "eligible"]
    scores = [r.get("cross_validation", {}).get("gpd_minus_exponential_per_excess") for r in tails]
    scores = [v for v in scores if v is not None]
    failures = sum(r.get("cross_validation", {}).get("models", {}).get("gpd", {}).get(
        "status") == "zero_predictive_density" for r in tails)
    return [f"{min(shapes):.4f} to {max(shapes):.4f}" if shapes else "not identified",
            f"{min(scores):+.5f} to {max(scores):+.5f}" if scores else "unavailable",
            f"{len(scores)}/{len(cells)}", failures]


def figures(report, output):
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.5), sharey=True)
    colors = ("#176b87", "#bb4430", "#7c699a")
    for ds, ax in zip(DATASETS, axes, strict=True):
        for condition, color in zip(CONDITIONS, colors, strict=True):
            cs = [c for c in report["cells"] if c["phase"] == "stage4" and c["dataset"] == ds
                  and c["condition"] == condition]
            for c in cs:
                s = c["survival"]
                x, y = np.array(s["x"]), np.array(s["probability"])
                keep = y > 0
                ax.plot(x[keep], y[keep], color=color, alpha=.16, lw=.6)
            c = next(c for c in cs if c["realization"] == 0 and c["order"] == 100)
            s = c["survival"]
            x, y = np.array(s["x"]), np.array(s["probability"])
            keep = y > 0
            ax.plot(x[keep], y[keep], color=color, lw=1.7, label=LABELS[condition])
        ax.set(xscale="log", yscale="log", xlabel="Loss increase threshold (nats)", title=NAMES[ds])
        ax.grid(alpha=.18)
        if ds != "zsre":
            ax.text(.04, .06, "Stable v0: no observed positive harm", transform=ax.transAxes, fontsize=8)
    axes[0].set_ylabel("Fraction of all positions above threshold")
    axes[0].legend(fontsize=8)
    fig.suptitle("Observed harm tails: bold r0/order100; faint all 15 cells per condition")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(output / f"harm-survival.{ext}", dpi=190, bbox_inches="tight")
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), sharey=True)
    for seed, ax in enumerate(axes):
        for rule, color in (("bp", "#176b87"), ("epc", "#bb4430")):
            t = next(t for t in report["training"] if t["rule"] == rule and t["seed"] == seed)
            y = np.array(t["series"]["preserve"])
            ax.plot(np.arange(1, 301), y, color=color, alpha=.25, lw=.7)
            ax.plot(np.arange(10, 301), np.convolve(y, np.ones(10) / 10, "valid"),
                    color=color, lw=1.5, label=rule.upper())
        ax.set(yscale="log", xlabel="Training update", title=f"Paired seed {seed}")
        ax.grid(alpha=.18)
    axes[0].set_ylabel("Mean preservation KL in the logged batch (nats)")
    axes[0].legend()
    fig.suptitle("Training preservation: faint individual updates; bold trailing 10-update mean")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(output / f"training-preservation.{ext}", dpi=190, bbox_inches="tight")
    plt.close(fig)


def render(report, source):
    grouped = {(g["phase"], g["condition"], g["dataset"]): g for g in report["groups"]}
    primary = [c for c in report["cells"] if c["phase"] == "stage4" and c["condition"] in CONDITIONS]
    lines = ["# Entropy, KL divergence, and the extremes in our experiments", "",
             "Prepared for charlie by Capex · 9 October 2026 · analysis of saved results, no model execution.", "",
             "**The tails depend on both the editing dataset and the kind of cap.** For the main learned cap, "
             "CounterFact and MQuAKE produce more frequent and more severe ordinary-text harm than zsRE. "
             "The clearest evidence for a heavier-than-exponential tail on the measured range remains **stable v0 on zsRE**. "
             "A larger maximum, a larger KL, or a larger Shannon entropy is not by itself evidence of a heavier tail.", "",
             "I measured **330 completed evaluation configurations, seven 300-update training histories, and nine "
             "cached teacher-logit populations**. The new MQuAKE analysis matters: its learned-cap harm is substantial, "
             "but its generalized-Pareto fit does not predict held-out extremes better than an exponential. "
             "The analysis also finds much larger logged preservation KL during ePC reader training than BP training, "
             "without a uniform corresponding change in evaluation harm. **The learned cap's KL tails on zsRE and "
             "CounterFact also show a heavier-than-exponential pattern at the lower thresholds, even though its "
             "actual-token harm tails are close to exponential.** Those are different random variables.", "",
             "The main limitation is explicit: **we did not save per-example training losses or cap-on vocabulary "
             "distributions for the full evaluation.** We can measure training-update averages and evaluation-position "
             "tails, and can recover the frozen teacher's predictive entropy from caches. We cannot reconstruct the "
             "missing within-batch extremes or cap-on predictive entropy from a scalar loss or KL.", "",
             "## 1. What is being measured?", "",
             "For a particular text prefix, GPT-2 assigns a probability to each of its 50,257 possible next tokens. "
             "Let p be that distribution without the cap, q the distribution with it, and y the actual next token.", "",
             "- **Loss / surprisal:** L = −ln q(y). A larger loss means the actual continuation received less probability. "
             "For a single known target, this is cross-entropy against a one-hot target; it is not Shannon entropy of q.",
             "- **Harm:** Δ = L(cap) − L(cap-off) = ln[p(y)/q(y)]. Positive values are worse; negative values are improvements. "
             "A five-nat increase means the actual token became about 148 times less likely; ten nats means about 22,026 times.",
             "- **Token-prediction KL:** D(p‖q) = Σ p(v) ln[p(v)/q(v)]. It measures how the whole next-token distribution "
             "changed, weighting tokens by the no-cap distribution. It is nonnegative apart from numerical roundoff. "
             "It is not the reverse divergence D(q‖p), and it is not the loss on just the actual token.",
             "- **Predictive Shannon entropy:** H(p) = −Σ p(v) ln p(v). It measures uncertainty across next-token choices. "
             "A distribution concentrated on one token has entropy near zero; a uniform distribution over the vocabulary "
             "has entropy ln(50,257) ≈ 10.8249 nats. High confidence can be correct or wrong.", "",
             "We also compute two explicitly different Shannon entropies below: entropy of **loss bins**, and entropy "
             "of **where the total positive loss is concentrated**. These answer questions about the losses, not the "
             "model's uncertainty over vocabulary tokens. All logarithms are natural and all entropy/KL values are nats.", "",
             "## 2. Evaluation: the dataset comparison", "",
             "These are **ordinary-text validation positions after editing with each named dataset**, not losses on "
             "that dataset's questions. Each cell scores the same 245,237 positions in 1,931 reset-context windows. "
             "Thus the dataset label identifies which facts were installed in the cap. It does not mean CounterFact "
             "and MQuAKE supplied the ordinary text being scored.", "",
             "There are fifteen main cells per condition/dataset: three subject realizations, each run in five orders. "
             "zsRE and CounterFact finish at 1,000 edits; MQuAKE at 300. These are useful observed-system comparisons, "
             "but the unequal edit counts prevent a clean causal claim that dataset identity alone caused the difference. "
             "Reused text positions and five orders are not independent replications.", "",
             "### Main learned cap: averages hide the extremes", ""]
    rows = []
    for ds in DATASETS:
        g = grouped["stage4", "R1_learned_ff", ds]
        d, k = g["metrics"]["delta_nll"], g["metrics"]["kl_capoff_to_cap"]
        rows.append([NAMES[ds], f(k["mean"]["mean"]), f(d["mean"]["mean"]),
                     f(100 * d["exceed_0.01"]["fraction"]) + "%", f(d["exceed_0.01"]["conditional_mean"]),
                     f(d["es99_positive"]["mean"]), f(d["maximum"]["maximum"])])
    lines += [table(["Editing dataset", "Mean KL", "Mean ΔNLL", "Positions with Δ > .01", "Mean Δ given Δ > .01",
                     "Mean cell ES99+", "Largest Δ, any cell"], rows), "",
              "**ES99+** is the average positive harm in the worst 1% of all positions, with zero and beneficial "
              "positions represented by zero. This differs from the conditional mean among harmed positions. "
              "Means in this table are equal-cell means; conditional severity weights by event counts; maxima take "
              "the largest observed position across cells. Full per-cell quantiles, including 99.9% and 99.99%, are saved.", "",
              "The learned cap's worst MQuAKE increase, 17.0605 nats, corresponds to about **25.7 million times less "
              "probability for that observed token**. That is a probability ratio at a fixed prefix, not 25.7 million "
              "wrong answers or a measured probability of real-world catastrophe.", "",
              "### All three main caps: frequency, severity and KL", ""]
    rows = []
    for ds in DATASETS:
        for cond in CONDITIONS:
            g = grouped["stage4", cond, ds]
            d, k = g["metrics"]["delta_nll"], g["metrics"]["kl_capoff_to_cap"]
            rows.append([NAMES[ds], LABELS[cond], f(100*d["exceed_0.01"]["fraction"]) + "%",
                         f(d["es99_positive"]["mean"]), f(d["maximum"]["maximum"]),
                         f(k["mean"]["mean"]), f(k["maximum"]["maximum"])])
    lines += [table(["Dataset", "Cap", "Harm frequency > .01", "ES99+", "Worst harm", "Mean KL", "Worst KL"], rows), "",
              "Stable v0's zero ordinary-text change on CounterFact and MQuAKE is an observed lack of intervention "
              "on this text population. Its paraphrase generalization is also zero there; zero harm does not establish "
              "a useful safe editor. The random reader's CounterFact result shows particularly frequent collateral change.", "",
              "![Observed harm survival by dataset](measurement-figures/harm-survival.png)", "",
              "Each curve shows the fraction of all positions with loss increase above the horizontal-axis threshold. "
              "Faint curves show all fifteen cells; bold curves are the outcome-independent illustrative choice "
              "realization 0/order 100. Zero survival is omitted from the logarithmic plot. Smooth connecting lines "
              "join a fixed threshold grid; their apparent straightness is not a power-law test.", "",
              "## 3. How heavy are the tails, as opposed to how large is the harm?", "",
              "The empirical frequency and severity above are direct measurements. To describe shape, we compare "
              "an exponential distribution with a generalized Pareto distribution (GPD) for positive excesses Δ−u. "
              "The GPD shape ξ is zero for an exponential, positive for a power-law tail, and negative for a finite "
              "endpoint *within that fitted model*. Fitting a positive ξ does not prove an asymptotic power law; "
              "fitting a negative ξ does not establish a real safety bound.", "",
              "The following table uses u = .01 nat, at least 100 exceedances in at least 30 windows, and five-fold "
              "held-out-window predictive likelihood. A positive score difference favors GPD; a negative difference "
              "favors the simpler exponential. A fitted endpoint that excludes a held-out observation causes a "
              "support failure, which remains visible rather than being dropped from a score.", ""]
    rows = []
    for ds in DATASETS:
        for cond in CONDITIONS:
            cs = [c for c in primary if c["dataset"] == ds and c["condition"] == cond]
            rows.append([NAMES[ds], LABELS[cond], *shape_row(cs, "tail_fits")])
    lines += [table(["Dataset", "Cap", "Fitted ξ range", "GPD − exponential nats/excess", "Valid comparisons", "Cells with support failure"], rows), "",
              "**Interpretation:**", "",
              "- **Stable v0, zsRE:** consistently positive shapes and better held-out GPD predictions support a "
              "heavier tail over the measured range. The illustrative shape's existing 95% window-bootstrap interval "
              "is about 0.390–0.779. This is our strongest such finding, not a measurement of infinite variance.",
              "- **Learned cap, zsRE and CounterFact:** small shape estimates and little predictive advantage for GPD "
              "support an economical exponential approximation over the observed range. Existing illustrative shape "
              "intervals include zero. This is not an equivalence test or a proof of an exponential asymptotic tail.",
              "- **Learned cap, MQuAKE:** all fifteen primary-threshold shapes are negative. The illustrative interval "
              "is approximately −0.235 to −0.044, but all fifteen held-out predictive comparisons favor the exponential. "
              "Therefore the negative fit is not a validated hard ceiling. At thresholds .5 and 1, fourteen of fifteen "
              "GPD comparisons fail on held-out support; the remaining comparison favors the exponential.",
              "- **Random reader, MQuAKE:** every primary-threshold fitted endpoint excludes held-out observations. "
              "The negative shape estimates cannot be used to promise bounded harm.",
              "- **Zero/sparse cases:** a tail family is unidentifiable with no or too few observed events. "
              "That is an evidence limit, not a declaration of a light tail.", "",
              "The examination of MQuAKE's 45 harm-tail distributions and all 135 primary-cell KL distributions below is **new exploratory "
              "post-freeze analyses of saved vectors**. The zsRE/CounterFact harm fits reuse the completed HT-17 "
              "record. This does not change the registered experiments, thresholds, selected readers or claims. "
              "All four thresholds (.01, .1, .5, 1) remain in the numerical output. Bootstrap intervals use 200 "
              "whole-window resamples, not independent tokens; they still omit uncertainty over new subjects/training "
              "seeds and possible dependence between windows.", "",
              "### KL has its own tail", "",
              "These are fits to per-position D(cap-off‖cap), not to the actual-token loss change. Two quantities "
              "can be related without having identical extreme events or fitted shapes.", ""]
    rows = []
    for ds in DATASETS:
        for cond in CONDITIONS:
            cs = [c for c in primary if c["dataset"] == ds and c["condition"] == cond]
            rows.append([NAMES[ds], LABELS[cond], *shape_row(cs, "kl_tail_fits")])
    lines += [table(["Dataset", "Cap", "KL-tail ξ range", "GPD − exponential nats/excess", "Valid comparisons", "Cells with support failure"], rows), "",
              "**A new distinction:** the learned cap's KL-tail shapes are positive on both zsRE and CounterFact, "
              "and GPD predicts held-out KL excesses better in all fifteen cells of each dataset at u=.01. "
              "For the illustrative cells, shape intervals are approximately **0.149–0.400 (zsRE)** and "
              "**0.251–0.547 (CounterFact)**. MQuAKE's illustrative interval, **−0.076–0.217**, includes zero, "
              "and all fifteen MQuAKE predictive comparisons favor the exponential.", "",
              "This is evidence about the lower-threshold finite-range **KL** tail, not proof of an asymptotic "
              "class. Threshold sensitivity is material: the illustrative learned-cap KL shapes at u=.01/.1/.5/1 "
              "are **.274/.351/.119/−.157 for zsRE** and **.393/.481/.052/−.107 for CounterFact**. "
              "Thus a single positive shape at .01 should not be extrapolated indefinitely into the extremes. "
              "Read these alongside the worst-KL column: shape describes the decay of exceedances; the worst "
              "observed value describes a particular finite sample. Neither supplies the other.", "",
              "## 4. Shannon entropy: what we could actually recover", "",
              "### Genuine predictive entropy of cached frozen-GPT-2 distributions", "",
              "The reader-training feature banks retained full **cap-off** vocabulary logits for preservation "
              "prompts, quantized to float16. I normalized those logits in float64 and computed H(p). These are "
              "real cached predictions used as training teachers, not new model calls. The locality-cache split is "
              "the implemented 90%/10% item split: 900/100 items for zsRE and CounterFact, 450/50 for MQuAKE. "
              "CounterFact and MQuAKE have up to two locality rows per item. Repeated locality prompts remain "
              "repeated slots in the mean; the unique-prefix column discloses this dependence.", ""]
    rows = []
    for c in report["cached_teacher_entropy"]:
        e = c["entropy"]
        rows.append([NAMES.get(c["dataset"], "Ordinary text") + (f" seed {c['seed']}" if c["seed"] is not None else ""),
                     c["population"].replace("-cache", ""), e["n"], c["unique_token_prefixes"], f(e["mean"]),
                     f(e["minimum"]), f(e["quantiles"]["0.99"]), f(e["maximum"])])
    lines += [table(["Population", "Split/prompt role", "Rows", "Unique prefixes", "Mean H", "Min H", "p99 H", "Max H"], rows), "",
              "MQuAKE locality-cache prompts have higher mean teacher entropy than zsRE locality-cache prompts. "
              "That is a comparison of these differently constructed prompt pools, not proof that MQuAKE edits "
              "cause higher predictive uncertainty or heavier harm tails. Ordinary-text rows sample 512 windows "
              "at prefix lengths 16, 48 and 96 for each training seed; they are from the training text range, not "
              "the 1,931-window validation assay.", "",
              "The JSON also reports D(p‖uniform vocabulary) = ln(50,257) − H(p). That KL measures peakedness "
              "relative to a uniform vocabulary, **not** preservation error or cap-induced harm. The cached held-out "
              "rows are reader-training holdouts, not a newly untouched final test set.", "",
              "**Unavailable from the retained data:** H(q), the change H(q)−H(p), and reverse token KL on the full "
              "validation population. The saved five-field arrays contain three losses and two forward KLs, not "
              "full logits. Loss and forward KL do not uniquely determine those missing entropies. A future replay "
              "could record them, but no post-deadline model run was added here.", "",
              "### Entropy of the allocation of harm", "",
              "Let hᵢ = max(Δᵢ,0), and normalize the total positive harm into weights wᵢ = hᵢ / Σh. "
              "Then H(w) = −Σwᵢ ln wᵢ answers: **is the damage spread across many positions or concentrated in a few?** "
              "exp(H) is the effective number of equal-harm positions. D(w‖uniform positions) = ln(N)−H(w) "
              "is larger when harm is more concentrated. If total harm is zero, these quantities are undefined, "
              "not zero. Multiplying all harms by ten leaves this entropy unchanged, so severity must be reported separately.", ""]
    rows = []
    for ds in DATASETS:
        for cond in CONDITIONS:
            c = next(c for c in primary if c["dataset"] == ds and c["condition"] == cond and
                     c["realization"] == 0 and c["order"] == 100)
            m = c["metrics"]["delta_nll"]["positive_mass"]
            rows.append([NAMES[ds], LABELS[cond], f(m["entropy_nats"]), f(m["effective_positions"]),
                         f(m["kl_to_uniform_nats"]), m["half_mass_positions"] or "undefined",
                         "undefined" if m["top_0_1_percent_mass_share"] is None else f(100*m["top_0_1_percent_mass_share"]) + "%"])
    lines += [table(["Dataset", "Cap (r0/o100)", "H(harm allocation)", "Effective positions", "KL to uniform positions",
                     "Positions carrying half of harm", "Harm carried by worst 0.1%"], rows), "",
              "The denominator is 245,237 positions in every row. The worst 0.1% means 245.237 positions with a "
              "fractional boundary weight. This entropy is a concentration diagnostic, not a fitted tail exponent.", "",
              "### Entropy and KL of binned loss values", "",
              "For completeness, absolute NLLs were placed into the same bins for cap-on and cap-off: "
              "[0,.01), [.01,.1), [.1,.5), [.5,1), [1,2), [2,3), [3,5), [5,8), [8,12), [12,20), "
              "[20,40), [40,80), [80,∞). H is the Shannon entropy of these bin frequencies. "
              "The following KL compares **loss histograms**, not next-token distributions.", ""]
    rows = []
    for ds in DATASETS:
        c = next(c for c in primary if c["dataset"] == ds and c["condition"] == "R1_learned_ff" and
                 c["realization"] == 0 and c["order"] == 100)
        a, b = c["metrics"]["cap_nll"], c["metrics"]["capoff_nll"]
        comparison = c["loss_histogram_cap_to_capoff"]
        rows.append([NAMES[ds], f(b["positive_histogram"]["entropy_nats"]), f(a["positive_histogram"]["entropy_nats"]),
                     f(comparison["smoothed"]["0.5"]["a_to_b"]), f(b["maximum"]), f(a["maximum"])])
    lines += [table(["Learned cap r0/o100", "H(base loss bins)", "H(cap loss bins)", "KL(cap bins‖base bins), α=.5",
                     "Max base NLL", "Max cap NLL"], rows), "",
              "Histogram KL uses a disclosed half-count pseudocount in each bin; the JSON retains raw divergence "
              "and sensitivity to α=.1 and 1, plus Jensen–Shannon divergence. Empty support produces infinite raw "
              "KL, stored as an explicit status rather than a misleading finite value. All these results depend on "
              "binning. They can look almost unchanged because most positions are unchanged, even when rare paired "
              "harm is large. The worst absolute NLL also need not occur where the cap causes the worst extra loss.", "",
              "## 5. Training: measurable spikes, but missing within-batch tails", "",
              "Each of the seven runs saved 300 updates. An entry's `preserve` value is an **average of per-episode "
              "means across the two episodes in that update**, not the largest token KL and not necessarily the "
              "prefix-count-weighted mean across both episodes. Training mixes all three editing datasets with "
              "ordinary-text nulls, and the log does not separate their contributions. Dataset-specific training "
              "loss tails therefore cannot be reconstructed from these scalar averages.", "",
              "BP and ePC seeds 0/1/2 have matching recorded episode identities at every update. The preservation "
              "diagnostic uses forward KL under current writes in both rules, but BP uses its cached float16 teacher "
              "and ePC recomputes the teacher in float32. ePC's logged answer CE is from settled states, whereas "
              "BP's is feedforward CE. The training reader uses a soft episodic path; evaluation uses the selected "
              "checkpoint average, acquired memory and hard gating. These differences rule out treating every "
              "training-versus-evaluation scalar as the same population or prediction process.", ""]
    rows = []
    for t in report["training"]:
        a, b, full = (t["windows"][w]["preserve"] for w in ("first50", "last50", "all300"))
        rows.append([t["rule"], t["seed"], f(a["mean"]), f(b["mean"]), f(full["quantiles"]["0.99"]),
                     f(full["maximum"]), full["maximum_step_one_based"]])
    lines += [table(["Training run", "Seed", "First 50 mean KL", "Last 50 mean KL", "p99 update KL (all300)",
                     "Largest update-mean KL", "Update of maximum"], rows), "",
              "The ePC runs have considerably larger preservation-KL update means and upper extremes than their "
              "paired BP runs. This is a diagnostic concern, not proof of universally worse deployment behavior: "
              "the evaluation pattern depends on dataset and seed, as shown below. Nor does the training trace "
              "identify a power-law family. The parameter state changes throughout training, making these 300 values "
              "a dependent, nonstationary trajectory rather than independent draws from a fixed distribution.", "",
              "![Training preservation-KL trajectories](measurement-figures/training-preservation.png)", "",
              "### Other saved training losses and the common holdout diagnostic", ""]
    rows = []
    for t in report["training"]:
        a, rr = (t["windows"]["last50"][k] for k in ("answer", "retrieval"))
        lastdev = t["dev"][-1]
        rows.append([t["rule"], t["seed"], t["diagnostic"], f(a["mean"]), f(a["maximum"]),
                     f(rr["mean"]), f(lastdev["dev_retrieval"])])
    lines += [table(["Run", "Seed", "Answer diagnostic", "Last50 answer mean", "Last50 answer max",
                     "Last50 retrieval mean", "Step300 held-out retrieval"], rows), "",
              "Answer diagnostics are deliberately labelled rather than ranked against each other. The original "
              "selected-v5 history also retained held-out answer and preservation **means** every fifty updates; "
              "the six supplemental runs retained only the common held-out retrieval mean at those checkpoints. "
              "Six averaged holdout measurements cannot reveal per-example extremes. They refer to raw checkpoints; "
              "the deployed reader is the specified tensor average of steps 150/200/250/300.", "",
              "### Shannon entropy and KL of the logged training-loss distributions", "",
              "These values describe preservation-KL **update means placed in the loss bins from §4**. "
              "The last column is KL between late and early distributions of those means, using α=.5 per bin. "
              "It is a second level of KL calculation: distributional change of a recorded diagnostic, rather "
              "than another vocabulary-level KL.", ""]
    rows = []
    for t in report["training"]:
        a = t["windows"]["all300"]["preserve"]["positive_histogram"]["entropy_nats"]
        b = t["windows"]["last50"]["preserve"]["positive_histogram"]["entropy_nats"]
        k = t["late_to_early_histogram"]["preserve"]["smoothed"]["0.5"]["a_to_b"]
        rows.append([t["rule"], t["seed"], f(a), f(b), f(k)])
    lines += [table(["Run", "Seed", "H(update-loss bins), all300", "H(update-loss bins), last50",
                     "KL(last50 bins‖first50 bins)"], rows), "",
              "Higher H here means the update means occupy more of these particular bins; it does not identify "
              "a power law or establish that a learning algorithm is better. The numerical record includes "
              "Shannon entropy of the binned training-update values and their "
              "normalized loss-mass concentration, separately for all300, first50, last50 and last150. It also "
              "includes late-versus-early histogram KL with three pseudocounts. These quantify the logged trajectory, "
              "not hidden per-example loss tails. I have not reported a train-versus-test loss-histogram KL: mixing "
              "batch-average training metrics, settled CE, and token-level validation losses would make that number misleading.", "",
              "## 6. Later controls: do the tails improve?", ""]
    rows = []
    for g in report["groups"]:
        if g["phase"] != "PC-reader":
            continue
        d, k = g["metrics"]["delta_nll"], g["metrics"]["kl_capoff_to_cap"]
        rows.append([NAMES[g["dataset"]], g["condition"].upper(), g["cells"], f(k["mean"]["mean"]),
                     f(d["es99_positive"]["mean"]), f(d["maximum"]["maximum"]),
                     f(100*d["exceed_0.01"]["fraction"]) + "%"])
    lines += [table(["Dataset", "Reader training", "Seeds", "Mean evaluation KL", "Mean ES99+", "Worst harm", "Harm frequency >.01"], rows), "",
              "These paired evaluations use the same exposed realization/order at 300 edits. There is no MQuAKE "
              "BP/ePC reader comparison in this supplemental study. Three training seeds do not replace independent "
              "subject populations, and the aggregate is not a claim of a universal training-rule effect.", ""]
    rows = []
    for g in report["groups"]:
        if g["phase"] != "AW-B" or g["condition"] == "capoff":
            continue
        d, k = g["metrics"]["delta_nll"], g["metrics"]["kl_capoff_to_cap"]
        rows.append([NAMES[g["dataset"]], g["condition"], f(k["mean"]["mean"]),
                     f(d["es99_positive"]["mean"]), f(d["maximum"]["maximum"])])
    lines += ["### The explicit one-nat intervention", "",
              table(["Dataset", "AW-B arm (five memories)", "Mean KL", "Mean ES99+", "Worst harm"], rows), "",
              "The mixture uses q_mix = ρp + (1−ρ)q with ρ=e⁻¹. Since q_mix(v)≥ρp(v), "
              "ln[p(v)/q_mix(v)]≤1 for every token with positive p(v). Therefore both actual-token harm and "
              "D(p‖q_mix) have a one-nat upper bound at the same prefix, apart from numerical tolerance. "
              "This is an algebraic bound, stronger evidence for bounded harm than a fitted negative tail shape. "
              "It does not bound the absolute NLL, multi-step generation harm, or every behavioral failure. "
              "See the [AW-B report](../../pc_cap/docs/additional_work/AW-B_report.md) for efficacy tradeoffs.", "",
              "The numerical inventory additionally measures the eighteen distinct new AW-L cells; six shared "
              "full-read/full-write controls are counted once in PC-reader. The existing "
              "[AW-L report](../../pc_cap/docs/additional_work/AW-L_report.md) shows that restricting writes to the "
              "last site increased mean loss harm in every paired comparison. Upper layers should not be assumed "
              "safer merely because they are closer to the output.", "",
              "## 7. What to say about the extremes—and what to measure next", "",
              "A defensible presentation sentence is: **‘Collateral prediction loss is usually absent, but rare "
              "events can be severe. Their frequency, severity and fitted tail shape depend on the cap and the "
              "editing dataset. Stable v0 on zsRE gives the strongest evidence for a heavier-than-exponential "
              "harm tail over our measured range. The learned cap has damaging extremes and heavier lower-threshold "
              "KL tails on zsRE/CounterFact, without establishing an asymptotic power-law class. "
              "An explicit probability mixture bounds per-prefix harm.’**", "",
              "This evidence does **not** establish super-linear MQuAKE cascades, linear zsRE scaling, equilibrium "
              "classes, or a separate tail family for each benchmark. In particular, the broad assertions in "
              "[extreme-ish.md](extreme-ish.md) and [harm-in-detail.md](harm-in-detail.md) should not be used as "
              "measured findings: zsRE did have locality, near-miss, unseen and revision endpoints; the learned "
              "reader did not pass every fidelity/harm criterion; and the frozen weights can stay unchanged while "
              "the **capped system's** predictions are harmed. Those other documents are not modified here.", "",
              "For a later experiment, the most useful extra logging would be:", "",
              "1. Save each training prefix's dataset, role, step, target NLL, forward/reverse KL, H(base), H(cap), "
              "and gate state, with item/window identities. Record these scalars during existing forward passes; "
              "full 50,257-way logits need not be retained for every prefix.",
              "2. At fixed checkpoints, use the same feedforward diagnostic on fixed training and genuinely held-out "
              "prefixes. Retain per-prefix values and keep settled ePC diagnostics in separate fields. That permits "
              "a meaningful training/test tail comparison and dataset attribution.",
              "3. Expand independent subject populations and text/document blocks, and use equal edit budgets when "
              "comparing datasets. Test tail-shape sensitivity to thresholds and block definitions before making "
              "an asymptotic claim. More reruns of the same text positions are not new independent extremes.",
              "4. Examine severe KL events and severe actual-token harm together, including low-entropy confident "
              "errors. Compare severity reductions with editing/paraphrase success, so a cap that never fires does "
              "not win simply by doing nothing.", "",
              "No training, GPU execution, checkpoint changes or new outcome-based selection was performed for "
              "this document. This is a post hoc analysis after the October 9 experimental cutoff; future model "
              "execution belongs to a later study.", "",
              "## 8. Reproducibility and exact sources", "",
              f"- [Complete numerical measurements](../../pc_cap/{source.relative_to(ROOT).as_posix()}): every cell, "
              "quantile, histogram, fit, training trace, cached-logit summary and input SHA-256 (gzip-compressed JSON).",
              f"- [Readable per-cell CSV](../../pc_cap/{source.parent.relative_to(ROOT).as_posix()}/cells.csv) "
              f"and [input hashes](../../pc_cap/{source.parent.relative_to(ROOT).as_posix()}/sources.json).",
              "- [Measurement code](../../pc_cap/aw/entropy_tail_measurements.py), "
              "[report/figure builder](../../pc_cap/aw/entropy_tail_report.py), and "
              "[focused tests](../../pc_cap/aw/tests/test_entropy_tail_measurements.py).",
              "- [270-cell source inventory](../../pc_cap/logs/additional_work/round48/HT-15b-270/cell_tails.json), "
              "[existing HT-17 fits](../../pc_cap/logs/additional_work/HT-17/snapshot-20261004-complete/report.json), "
              "[AW-L inventory](../../pc_cap/logs/additional_work/AW-L/report-round63-final/report.json).",
              "- [Historical selected-v5 training log](../../pc_cap/results/R1/pilot/r1_50_stream_sel6_text_s2/metrics.jsonl). "
              "Supplemental training logs are linked individually below.", ""]
    for t in report["training"]:
        if t["rule"] != "historical-v5-bp":
            relative = Path(t["path"]).relative_to(ROOT).as_posix()
            lines.append(f"- [{t['rule'].upper()} seed {t['seed']} training log](../../pc_cap/{relative}).")
    lines += ["", "Example source vectors for the main learned cap (realization 0/order 100):", ""]
    for ds in DATASETS:
        c = next(c for c in primary if c["dataset"] == ds and c["condition"] == "R1_learned_ff" and
                 c["realization"] == 0 and c["order"] == 100)
        relative = Path(c["vector"]["path"]).relative_to(ROOT).as_posix()
        lines.append(f"- [{NAMES[ds]} saved paired losses and KL](../../pc_cap/{relative}).")
    lines += ["", "Inventory scope: 270 Stage-4 cells + 12 PC-reader evaluations + 30 AW-B memory/arm "
              "combinations + 18 distinct new AW-L evaluations = 330. This is not a claim to reanalyze every "
              "historical pilot or every acquisition-credit study; those have their own reports. The 330 records "
              "reuse text and include controls, not 330 independent populations. Within the primary conditions, "
              "all fifteen cells per dataset are included, including all forty-five MQuAKE cells omitted from "
              "HT-17's main Stage-4 population.", "",
              "Commands from `/home/derp/cap/pc_cap` (choose a fresh output directory):", "", "```bash",
              "JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \\",
              "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ../venv/bin/python \\",
              "  -m aw.entropy_tail_measurements --output logs/entropy-tail-measurements-NEW", "",
              "MPLCONFIGDIR=/tmp/capex-measurements-mpl OPENBLAS_NUM_THREADS=1 \\",
              "PYTHONDONTWRITEBYTECODE=1 python3 -m aw.entropy_tail_report \\",
              "  --input logs/entropy-tail-measurements-NEW/measurements.json.gz \\",
              "  --document ../assets/support-information/measurements.md \\",
              "  --figures ../assets/support-information/measurement-figures", "```", "",
              f"The saved measurement pass used {report['wall_seconds']:.1f} seconds of wall time and "
              f"{report['peak_rss_mib']:.1f} MiB peak host RSS, with zero GPU seconds and zero model calls. "
              "Inputs were hashed before analysis; cached banks were loaded one at a time. The source vectors and "
              "frozen experimental records were not modified. JSON keeps undefined zero-mass entropy and invalid "
              "predictive fits distinct from numerical zero.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--figures", type=Path, required=True)
    args = parser.parse_args()
    source = args.input.resolve()
    raw = source.read_bytes()
    report = json.loads(gzip.decompress(raw) if source.suffix == ".gz" else raw)
    figures(report, args.figures)
    args.document.write_text(render(report, source))
    receipt = dict(report_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   outputs={str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [args.document, *sorted(args.figures.glob("*"))]})
    (source.parent / "document-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Wrote {args.document} and figures")


if __name__ == "__main__":
    main()
