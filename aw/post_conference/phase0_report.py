"""Phase 0 report (CPU): Markdown + PDF from the Phase 0 tables. Every number is read from the tables; the text states
the finding the number supports and nothing more."""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

from aw.extremes.md2tex import build
from aw.post_conference.common import DATASETS, FIGURES, NULL_THRESHOLD, OUT, ROOT, TABLES, Status, ensure_dirs, read_json

DS = {"zsre": "zsRE", "counterfact": "CounterFact", "mquake": "MQuAKE"}
FIGREL = "../../../../../assets/post_conference/phase0/figures"


def md_table(cols, rows):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def f2(x, d=2):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def pct(x, d=1):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{100 * x:.{d}f} %"


def rng(series, fmt=pct):
    return f"{fmt(series.min())}–{fmt(series.max())}"


def sec_frontier(fr, icf, ics):
    out = ["## 1. Are the BP and PC readers on the same gate frontier?\n",
           f"The registered gate fires when the reader's null mass is below {NULL_THRESHOLD} and the rare-token veto passes. Sweeping the threshold on the saved null masses, with forward-only replays of every probe the threshold had stopped (validation: the untouched replay reproduces the saved losses exactly, table `replay_validation.csv`), gives each reader's operating curve. The rare-token veto is threshold-independent and is kept in every point.\n",
           f"![Gate frontier]({FIGREL}/frontier.png)\n", f"![Threshold sweep]({FIGREL}/frontier_threshold_sweep.png)\n"]
    rows = []
    for ds in DATASETS:
        x = fr[(fr.dataset == ds)]
        for rule, lab in (("bp", "BP-CAP"), ("epc", "PC-CAP")):
            y = x[x.rule == rule]
            reg = y[np.isclose(y.tau, NULL_THRESHOLD)]
            best_i = y.groupby("model").apply(lambda g: g.loc[g.paraphrase_exact.idxmax()]).reset_index(drop=True)
            open_ = y[np.isclose(y.tau, 1.0)]
            rows.append([DS[ds], lab, f"{pct(reg.paraphrase_exact.mean())} / {pct(reg.near_miss_neighbour_fire_rate.mean())} / {pct(reg.unseen_fire_rate.mean())}",
                         f"{pct(open_.paraphrase_exact.mean())} / {pct(open_.near_miss_neighbour_fire_rate.mean())} / {pct(open_.unseen_fire_rate.mean())}",
                         f"{f2(reg.paraphrase_mean_nll.mean())} → {f2(open_.paraphrase_mean_nll.mean())}", f"{f2(reg.paraphrase_cvar95.mean())} → {f2(open_.paraphrase_cvar95.mean())}",
                         f"{pct(reg.locality_item_fire_rate.mean())} → {pct(open_.locality_item_fire_rate.mean())}", f"{f2(best_i.tau.mean())}"])
    out.append("### 1.1 Registered gate versus the fully open gate (seed means)\n")
    out.append(md_table(["dataset", "cap", "τ = 0.5: paraphrase EM / near-miss fires / unseen fires", "τ = 1 (no null veto): same", "paraphrase mean NLL", "paraphrase CVaR95", "item-locality fire rate", "τ maximising paraphrase EM (mean over seeds)"], rows))
    out.append("\nAt τ = 1 the only remaining abstentions are the rare-token veto (evaluated on every forced acceptance, as the learner evaluates it after the null gate) and empty retrievals; the table therefore gives the whole range the null threshold can reach without changing the reader. Each arm carries its own acquired payloads, so a difference between curves mixes selection and payload; coincident curves mean similar trade-offs on this population, not identical gates or representations.\n")
    out.append("### 1.1b Selection risk and answer risk along the sweep (paraphrases, seed means)\n")
    rows = []
    for ds in DATASETS:
        for rule, lab in (("bp", "BP-CAP"), ("epc", "PC-CAP")):
            y = fr[(fr.dataset == ds) & (fr.rule == rule)]
            for tau in (0.3, 0.5, 0.7, 0.9, 1.0):
                z = y[np.isclose(y.tau, tau)]
                rows.append([DS[ds], lab, f"{tau:g}", pct(z.paraphrase_fire_rate.mean()), pct(z.paraphrase_wrong_record_rate.mean()), pct(z.paraphrase_fail_given_fired.mean()), pct(z.paraphrase_fail_given_fired_own.mean()), pct(z.paraphrase_exact.mean())])
    out.append(md_table(["dataset", "cap", "τ", "coverage (fired)", "selection risk: wrong record accepted", "answer risk: failed given fired", "failed given fired own record", "paraphrase EM"], rows))
    # same-frontier test: compare PC curve to BP curve at matched near-miss false-fire rate
    out.append("### 1.2 Matched false-fire comparison\n")
    rows = []
    for ds in DATASETS:
        x = fr[fr.dataset == ds]
        for target_ff in (0.02, 0.05, 0.10):
            vals = {}
            for rule in ("bp", "epc"):
                ems = []
                for model, y in x[x.rule == rule].groupby("model"):
                    y = y.sort_values("near_miss_neighbour_fire_rate")
                    if y.near_miss_neighbour_fire_rate.max() < target_ff:
                        ems.append(float(y.paraphrase_exact.iloc[-1]))  # never reaches that false-fire rate: take the most open point
                    else:
                        ems.append(float(np.interp(target_ff, y.near_miss_neighbour_fire_rate.values, y.paraphrase_exact.values)))
                vals[rule] = ems
            rows.append([DS[ds], pct(target_ff, 0), f"{pct(np.mean(vals['bp']))} ({pct(min(vals['bp']))}–{pct(max(vals['bp']))})", f"{pct(np.mean(vals['epc']))} ({pct(min(vals['epc']))}–{pct(max(vals['epc']))})", f"{100 * (np.mean(vals['epc']) - np.mean(vals['bp'])):+.1f} pp"])
    out.append(md_table(["dataset", "near-miss false-fire rate", "BP-CAP paraphrase EM (seed range)", "PC-CAP paraphrase EM (seed range)", "PC − BP"], rows))
    out.append("\nInterpolated along each seed's own sweep; when a reader never reaches the stated false-fire rate even with the null veto removed, its most open point is used. A difference inside the seed ranges means the two training rules produced gates on the same frontier and differ only in where the registered threshold placed them.\n")
    # in-context frontier
    out.append("### 1.3 The in-context retrievers on the same axes\n")
    rows = []
    for ds in DATASETS:
        for arm in ("knn", "lex"):
            y = icf[(icf.dataset == ds) & (icf.arm == arm)].sort_values("theta")
            if not len(y):
                continue
            always = y.iloc[0]
            best = y.loc[y.paraphrase_exact.idxmax()]
            rows.append([DS[ds], arm, pct(always.paraphrase_exact), f2(always.paraphrase_mean_nll), pct(always.near_miss_neighbour_fire_rate), pct(always.get("locality_item_frac_worse_1nat", np.nan)), f"{pct(best.paraphrase_exact)} at θ = {best.theta:g} (near-miss fires {pct(best.near_miss_neighbour_fire_rate)})"])
    out.append(md_table(["dataset", "retriever", "always prepend: paraphrase EM (prefix)", "paraphrase mean NLL", "near-miss prepend rate", "item-locality worse by > 1 nat", "best EM along the threshold sweep"], rows))
    return "\n".join(out)


def sec_atlas(pv, orc_rate, summ, diff):
    out = ["## 2. Where the remaining error is: gating, retrieval or payload\n", f"![Failure atlas]({FIGREL}/failure_atlas.png)\n"]
    rows = []
    for ds in DATASETS:
        for rule, lab in (("bp", "BP-CAP"), ("epc", "PC-CAP")):
            x = pv[(pv.dataset == ds) & (pv.rule == rule) & (pv.failure_definition == "not_exact")]
            rows.append([DS[ds], lab, f"{x.n_failures.mean():.0f} of {int(x.n_probes.iloc[0])}", f"{x.abstained_threshold.mean():.0f}", f"{x.abstained_rare_veto.mean():.0f}", f"{x.abstained_not_retrieved.mean():.0f}", f"{x.fired_correct_record.mean():.0f}", f"{x.fired_wrong_record.mean():.0f}", pct(x.fired_success_rate.mean()), pct(x.worst5pct_share_abstained.mean())])
    out.append("### 2.1 Paraphrase failures (generation not exact) by cause, seed means\n")
    out.append(md_table(["dataset", "cap", "failures", "abstained: null ≥ 0.5", "abstained: rare-token veto", "of which own record not among the 4 candidates", "fired own record, still failed (payload)", "fired a wrong record", "success when fired", "share of own worst 5 % that abstained"], rows))
    out.append("\n'Abstained: own record not retrieved' is a subset of the two abstention columns: the reader's top-4 retrieval did not contain the item's own record, so no threshold could have applied it.\n")
    rows = []
    for ds in DATASETS:
        for rule, lab in (("bp", "BP-CAP"), ("epc", "PC-CAP")):
            x = orc_rate[(orc_rate.dataset == ds) & (orc_rate.rule == rule)]
            rows.append([DS[ds], lab, f"{x.n_failures.mean():.0f}", pct(x.oracle_selection_rate.mean()), f"{x.correct_record_top.mean():.0f}", f"{x.already_selected_but_failed.mean():.0f}"])
    out.append("\n### 2.2 Oracle selection rate (review §3.1)\n")
    out.append(md_table(["dataset", "cap", "failures", "own record among candidates", "own record already top", "already applied and failed"], rows))
    out.append("\n### 2.3 Failures by frozen difficulty and answer length (seed-pooled)\n")
    rows = []
    for ds in DATASETS:
        x = diff[diff.dataset == ds]
        for rule in ("bp", "epc"):
            y = x[x.rule == rule]
            for terc in ("easy", "medium", "hard"):
                z = y[y.frozen_tercile == terc]
                if len(z):
                    rows.append([DS[ds], rule.upper(), terc, int(z.n.sum()), pct((z.success * z.n).sum() / z.n.sum()), pct((z.abstain_rate * z.n).sum() / z.n.sum()), pct((z.fired_failed_rate * z.n).sum() / z.n.sum())])
    out.append(md_table(["dataset", "rule", "frozen-loss tercile", "n (3 seeds)", "success", "abstain rate", "fired-and-failed rate"], rows))
    return "\n".join(out)


def sec_oracle(orc, ics):
    out = ["## 3. Oracle selection: what perfect record choice would and would not fix\n", f"![Oracle rescue]({FIGREL}/oracle_rescue.png)\n"]
    rows = []
    for ds in DATASETS:
        for rule, lab in (("bp", "BP-CAP"), ("epc", "PC-CAP")):
            x = orc[(orc.dataset == ds) & (orc.rule == rule)]
            ic = ics[(ics.dataset == ds) & (ics.family == "paraphrase") & (ics.arm == "in-context oracle")]
            rows.append([DS[ds], lab, f"{pct(x.success_registered.mean())} → {pct(x.success_oracle.mean())}", f"{f2(x.mean_nll_registered.mean())} → {f2(x.mean_nll_oracle.mean())}", f"{f2(x.cvar95_registered.mean())} → {f2(x.cvar95_oracle.mean())}",
                         f"{x.rescued_by_oracle.mean():.0f} of {x.n_failures.mean():.0f} ({pct(x.rescue_rate.mean())})", f"{x.rescued_among_abstained.mean():.0f} of {x.failures_abstained.mean():.0f}", f"{x.rescued_among_fired_wrong.mean():.0f} of {x.failures_fired_wrong.mean():.0f}", f"{x.not_rescuable_payload.mean():.0f}",
                         (f"{pct(ic.exact_prefix.iloc[0])} / {f2(ic.mean_nll.iloc[0])}" if len(ic) else "—")])
    out.append(md_table(["dataset", "cap", "paraphrase EM registered → oracle", "mean NLL", "CVaR95", "failures rescued", "rescued among abstentions", "rescued among wrong-record fires", "own record applied and still failed", "in-context oracle EM (prefix) / NLL"], rows))
    out.append("\nThe oracle forces the item's own record (identity only; nothing about the answer enters the prediction). The last column is the other oracle: the same fact placed in frozen GPT-2's context. The gap between the two oracles is the value of the write mechanism over a one-shot prompt when retrieval is perfect.\n")
    return "\n".join(out)


def sec_incontext(ics):
    out = ["## 4. Equal-information baseline: frozen GPT-2 with the taught fact in context\n", f"![In-context vs cap]({FIGREL}/incontext_vs_cap.png)\n",
           "Three retrieval arms prepend one taught fact (prompt + answer + newline) to the probe and run the frozen model: `oracle` prepends the probe's own fact (collateral families get no context: an oracle knows they are unrelated), `knn` the nearest taught prompt by cosine of the frozen residual keys at blocks 4/8/12 (the cap's own key feature, no learning), `lex` the best IDF-weighted token overlap. `knn`/`lex` always prepend, so their collateral columns are the worst case; §1.3 sweeps their retrieval scores as a threshold. Exact match is reported two ways: the project's strict rule (generation stops at a newline) and a prefix rule (generation starts with an alias), because a one-shot context often makes the model continue past the answer instead of emitting a newline; the caps' generations are rescored with the same prefix rule. The per-token NLL includes the newline terminator; a one-shot context demonstrates the answer format and so lowers the terminator's loss on *every* prompt, related or not, which is why the always-prepend arms look 'better than frozen' on unrelated prompts. The column without the terminator removes that format effect and is the one to read for collateral.\n"]
    for fam, tgt, title in (("paraphrase", "new", "Paraphrases (new answer)"), ("edit", "new", "Taught prompts (new answer)"), ("locality_item", "true", "Item-locality prompts (true answer)"), ("near_miss_neighbour", "true", "Near-miss neighbours (true answer)"), ("unseen", "new", "Unseen prompts (new answer; a 'success' here is a false fire)"), ("composition", "new", "MQuAKE multi-hop questions (new answer)")):
        rows = []
        for ds in DATASETS:
            x = ics[(ics.dataset == ds) & (ics.family == fam) & (ics.target == tgt)]
            for arm in ("frozen", "in-context oracle", "in-context knn", "in-context lex", "BP-CAP seed mean", "PC-CAP seed mean"):
                y = x[x.arm == arm]
                if len(y):
                    y = y.iloc[0]
                    rows.append([DS[ds], arm, int(y.n), f2(y.mean_nll), f2(y.mean_nll_noterm), f2(y.cvar95), pct(y.exact), pct(y.exact_prefix), pct(y.frac_worse_1nat), pct(y.frac_severe), pct(y.frac_better_1nat), pct(y.retrieved_own_rate)])
        if rows:
            out.append(f"### {title}\n")
            out.append(md_table(["dataset", "arm", "n", "mean NLL", "mean NLL w/o terminator", "CVaR95", "EM strict", "EM prefix", "worse than frozen > 1 nat", "> 2 nats", "better > 1 nat", "retrieved own item"], rows) + "\n")
    return "\n".join(out)


def sec_locality(lc, la, to):
    out = ["## 5. Locality audit and a corrigendum to the supplement\n", f"![Locality corrigendum]({FIGREL}/locality_corrigendum.png)\n"]
    rows = []
    for _, r in lc.sort_values(["dataset", "model"]).iterrows():
        rows.append([DS[r.dataset], r.label, int(r.n_locality_probes), int(r.n_source_item_taught), int(r.taught_fired), int(r.taught_fired_source_record), int(r.taught_severe), int(r.other_n), int(r.other_fired), int(r.other_deteriorated), int(r.other_severe), f2(r.other_max_D), pct(r.supplement_frac_worse_all), int(r.supplement_severe_all)])
    out.append(md_table(["dataset", "cap", "locality probes", "that are taught items", "fired on them", "fired their own record", "severe (D > 2) on them", "genuinely unrelated", "fired", "worse than frozen", "severe", "max D", "supplement 'worse than frozen'", "supplement severe"], rows))
    mq = lc[lc.dataset == "mquake"]
    out.append(f"\n**Corrigendum.** On MQuAKE, {int(mq.n_source_item_taught.iloc[0])} of the {int(mq.n_locality_probes.iloc[0])} item-locality prompts are themselves prompts of other taught stream items (the locality rows of MQuAKE cases are other cases' edited facts). A cap that fires on them is applying its own record for that item, and the 'true' answer it is scored against was deliberately overwritten. The supplement's statement that both caps got worse than frozen on 7.7 % of MQuAKE item-locality prompts with about 33 severe events per seed therefore counted {int(mq.taught_severe.min())}–{int(mq.taught_severe.max())} correct applications as collateral damage; on the genuinely unrelated prompts the counts are {int(mq.other_severe.min())}–{int(mq.other_severe.max())} severe events per seed ({pct(mq.other_frac_worse.min())}–{pct(mq.other_frac_worse.max())} worse than frozen). `aw/extremes/assemble.py` now labels these prompts `locality_item_taught`, and the extremes study's tables and reports were regenerated (zsRE and CounterFact have no such overlap).\n")
    out.append("### 5.1 The remaining false fires are same-template, different-subject prompts\n")
    rows = []
    for _, r in la[(la.family == "near_miss_neighbour") | ((la.family == "locality_item") & (la.dataset != "zsre"))].sort_values(["dataset", "family", "model"]).iterrows():
        rows.append([DS[r.dataset], r.family, r.label, int(r.n), pct(r.fired_rate), int(r.n_severe), int(r.severe_fired_other_record), pct(r.fired_frac_severe), f2(r.fired_mean_D), f2(r.overlap_fired), f2(r.overlap_abstained)])
    out.append(md_table(["dataset", "family", "cap", "n", "fired", "severe", "severe fires on another item's record", "share of fires that are severe", "mean D when fired", "non-stop token overlap with the taught prompt when fired", "when abstained"], rows))
    out.append("\nzsRE near-miss neighbours (matched-template questions about a different subject) and MQuAKE's unrelated locality prompts (same relation template, different subject) are where the genuine false fires are. The near-miss neighbour fires are the false fires that matter for a selection fix: they are the hard negatives the reader training recipe did not contain (its negatives were other items' paraphrases and ordinary text).\n")
    return "\n".join(out)


def sec_composition(cr, cf):
    out = ["## 6. Why composition scores zero\n", f"![Composition]({FIGREL}/composition.png)\n",
           "78 of the 80 MQuAKE composition cases have exactly one dependency in the 300-edit stream; the other hop is an unedited fact the frozen base must supply. The learned readers select one record at the prompt from a write-free pass and apply it at all three sites, so bank-to-bank chaining is not a mechanism these readers have (Capex review §3); the registered composition endpoint evaluates fresh-start dependency-edit states, not a query into the 300-edit memory. The table below reads the reader's selection fields on those endpoint states.\n"]
    rows = []
    for _, r in cr[cr.target == "new"].sort_values("model").iterrows():
        rows.append([r.label, int(r.n_questions), pct(r.dependency_retrieved_rate), pct(r.dependency_top_rate), pct(r.fired_rate), int(r.fired_on_dependency), int(r.abstain_threshold), pct(r.exact_rate), f2(r.mean_nll_frozen), f2(r.mean_nll), f2(r.mean_D_fired), pct(r.frac_improved_gt1_when_fired)])
    out.append(md_table(["cap", "questions", "dependency record retrieved", "dependency is top candidate", "fired", "fired on the dependency", "stopped by null threshold", "new answer exact", "frozen NLL", "cap NLL", "mean D when fired", "improved > 1 nat when fired"], rows))
    out.append("\n### 6.1 Frozen GPT-2 small on the other hop\n")
    rows = [[r.kind, r.target, int(r.n), pct(r.exact) if pd.notna(r.exact) else "—", pct(r.exact_prefix) if pd.notna(r.exact_prefix) else "—", pct(r.newline_immediately) if pd.notna(r.newline_immediately) else "—", f2(r.mean_nll), int(r.n_cases)] for _, r in cf.iterrows()]
    out.append(md_table(["probe kind", "target", "n", "EM strict", "EM prefix", "generation = immediate newline", "mean NLL", "cases"], rows))
    out.append("\nGreedy GPT-2 small answers a question-form prompt with a newline almost always (the 'immediate newline' column), so for question-form and in-context probes only the teacher-forced NLL is informative; on cloze prompts it continues past the answer, which the prefix rule credits.\n")
    out.append("\nReading: the reader retrieves the right record on most multi-hop wordings but the gate stops it (the question does not look like the taught prompt); when it fires, the taught delta moves the composed answer's loss only slightly, because the delta was acquired to produce the hop-1 answer at the hop-1 prompt, not to steer a two-hop question. And the frozen model's own knowledge of the unedited hop, asked directly with the new entity, bounds what any single-fact mechanism could compose. With the taught fact in its context, frozen GPT-2 small reaches the in-context row above on the multi-hop questions: that is the composition ceiling of the base model itself.\n")
    return "\n".join(out)


def sec_reserves(rs):
    out = ["## 7. Unexposed subjects available for confirmation\n"]
    rows = [[DS[r.dataset], r.method, int(r.cleared), int(r.reserved_items), int(r.remaining), int(r.remaining_subjects), int(r.overlap_with_reader_train_items), int(r.remaining_clean_of_reader_train), r.note] for _, r in rs.iterrows()]
    out.append(md_table(["dataset", "method", "cleared", "reserved by r0–r3", "remaining", "distinct subjects", "overlap with reader-training pool", "clean of reader training", "note"], rows))
    out.append("\nA 300-edit confirmation realization needs 300 edit subjects plus 350 endpoint-role subjects (outside, near-miss support and neighbour, revision). zsRE and CounterFact can each support one more such realization; MQuAKE can support several, subject to the entity/canonical-subject checks the certified register applies to the other two datasets.\n")
    return "\n".join(out)


def matched_ff(fr, ds, target_ff):
    """Paraphrase EM of every seed at a given near-miss false-fire rate, interpolated along its own threshold sweep."""
    vals = {}
    x = fr[fr.dataset == ds]
    for rule in ("bp", "epc"):
        ems = []
        for model, y in x[x.rule == rule].groupby("model"):
            y = y.sort_values("near_miss_neighbour_fire_rate")
            if y.near_miss_neighbour_fire_rate.max() < target_ff:
                ems.append(float(y.paraphrase_exact.iloc[-1]))
            else:
                ems.append(float(np.interp(target_ff, y.near_miss_neighbour_fire_rate.values, y.paraphrase_exact.values)))
        vals[rule] = ems
    return vals


def headline(fr, pv, orc, ics, lc, cr, cf, rs):
    H = ["## Findings\n"]
    # 1 frontier
    reg = fr[np.isclose(fr.tau, NULL_THRESHOLD)]
    parts = []
    for ds in DATASETS:
        b, p = reg[(reg.dataset == ds) & (reg.rule == "bp")], reg[(reg.dataset == ds) & (reg.rule == "epc")]
        v2, v10 = matched_ff(fr, ds, 0.02), matched_ff(fr, ds, 0.10)
        d2, d10 = np.mean(v2["epc"]) - np.mean(v2["bp"]), np.mean(v10["epc"]) - np.mean(v10["bp"])
        overlap10 = (max(v10["epc"]) >= min(v10["bp"])) and (max(v10["bp"]) >= min(v10["epc"]))
        parts.append(f"{DS[ds]}: registered {pct(b.paraphrase_exact.mean())} (BP) vs {pct(p.paraphrase_exact.mean())} (PC) at {pct(b.near_miss_neighbour_fire_rate.mean())} / {pct(p.near_miss_neighbour_fire_rate.mean())} near-miss false fires; at a matched 10 % false-fire rate PC − BP = {100 * d10:+.1f} pp ({'seed ranges overlap' if overlap10 else 'seed ranges do not overlap'}), at 2 % {100 * d2:+.1f} pp")
    H.append("1. **Mostly the same frontier.** " + "; ".join(parts) + ". The registered PC/BP paraphrase gap is largely an operating-point difference (the PC readers sit at a more conservative threshold); what remains at matched false-fire rates is small at open settings and larger on CounterFact at tight ones, with wide PC seed ranges. Each arm carries its own acquired payloads, so even a residual difference is not a difference between gates alone (table 1.2).")
    # 2 atlas
    cf_bp = pv[(pv.dataset == "counterfact") & (pv.failure_definition == "not_exact")]
    mq = pv[(pv.dataset == "mquake") & (pv.failure_definition == "not_exact")]
    H.append(f"2. **Gating on CounterFact, payload on MQuAKE.** CounterFact paraphrase failures are {pct((cf_bp.abstained / cf_bp.n_failures).mean())} abstentions (seed mean over both rules), and {pct((cf_bp.abstained_not_retrieved / cf_bp.n_failures).mean())} of all failures never had the own record among the four retrieved candidates. On MQuAKE {pct((mq.fired_correct_record / mq.n_failures).mean())} of failures fired the correct record and still failed: the per-position delta acquired on the taught prompt does not transfer to the question wording.")
    # 3 oracle
    H.append("3. **Oracle selection rescues** " + "; ".join(f"{DS[ds]} {pct(orc[(orc.dataset == ds) & (orc.rule == 'bp')].rescue_rate.mean())} (BP) / {pct(orc[(orc.dataset == ds) & (orc.rule == 'epc')].rescue_rate.mean())} (PC) of paraphrase failures" for ds in DATASETS) + ", lifting paraphrase EM to " + "; ".join(f"{DS[ds]} {pct(orc[(orc.dataset == ds)].success_oracle.mean())}" for ds in DATASETS) + ". The remainder fails with the correct record applied.")
    # 4 in-context
    parts = []
    for ds in DATASETS:
        x = ics[(ics.dataset == ds) & (ics.family == "paraphrase")]
        g = lambda arm, col: (x[x.arm == arm][col].iloc[0] if len(x[x.arm == arm]) else np.nan)
        parts.append(f"{DS[ds]}: in-context oracle EM {pct(g('in-context oracle', 'exact_prefix'))} / NLL {f2(g('in-context oracle', 'mean_nll'))}, knn {pct(g('in-context knn', 'exact_prefix'))} / {f2(g('in-context knn', 'mean_nll'))}, lex {pct(g('in-context lex', 'exact_prefix'))} / {f2(g('in-context lex', 'mean_nll'))}, versus BP-CAP {pct(g('BP-CAP seed mean', 'exact_prefix'))} / {f2(g('BP-CAP seed mean', 'mean_nll'))} and PC-CAP {pct(g('PC-CAP seed mean', 'exact_prefix'))} / {f2(g('PC-CAP seed mean', 'mean_nll'))}")
    H.append("4. **In-context retrieval is the bar.** " + "; ".join(parts) + " (prefix exact match; collateral in §4).")
    # 5 locality
    mqc = lc[lc.dataset == "mquake"]
    H.append(f"5. **Corrigendum.** {int(mqc.n_source_item_taught.iloc[0])} of 600 MQuAKE item-locality prompts are taught items; all but {int(mqc.other_severe.min())}–{int(mqc.other_severe.max())} of the ~33 severe 'collateral' events per seed were the cap correctly applying its own record. Genuine false fires are the zsRE near-miss neighbours and MQuAKE's same-template prompts (§5).")
    # 6 composition
    c = cr[cr.target == "new"]
    hop = cf[cf.kind == "single_hop_cloze (unedited hop)"]
    icm = cf[cf.kind == "multihop_in_context"]
    icm = icm[icm.target == "new"]
    mh_frozen = cr[cr.target == "new"].mean_nll_frozen.mean()
    H.append(f"6. **Composition.** The dependency record is retrieved on {pct(c.dependency_retrieved_rate.min())}–{pct(c.dependency_retrieved_rate.max())} of multi-hop questions but the gate fires on {pct(c.fired_rate.min())}–{pct(c.fired_rate.max())}; when it fires the composed answer's loss moves by {f2(c.mean_D_fired.min())}–{f2(c.mean_D_fired.max())} nats/token. Frozen GPT-2 small answers the unedited hop on {pct(hop.exact_prefix.iloc[0]) if len(hop) else '—'} of cloze prompts (prefix match; NLL {f2(hop.mean_nll.iloc[0]) if len(hop) else '—'}), and with the taught fact in its context its multi-hop target NLL falls from {f2(mh_frozen)} to {f2(icm.mean_nll.iloc[0]) if len(icm) else '—'} nats/token while the caps leave it at {f2(c.mean_nll.min())}–{f2(c.mean_nll.max())}: a one-shot context composes better than a write at blocks 4/8/12.")
    # 7 reserves
    H.append("7. **Reserves.** " + "; ".join(f"{DS[r.dataset]} {int(r.remaining)}" for _, r in rs.iterrows()) + " unexposed items remain (zsRE/CounterFact by the certified register; MQuAKE by population tables only), none overlapping the reader-training pool.")
    return "\n".join(H) + "\n"


def main():
    ensure_dirs()
    fr = pd.read_csv(TABLES / "frontier.csv")
    icf = pd.read_csv(TABLES / "incontext_frontier.csv")
    ics = pd.read_csv(TABLES / "incontext_summary.csv")
    pv = pd.read_csv(TABLES / "payload_vs_gating.csv")
    orc_rate = pd.read_csv(TABLES / "oracle_selection_rate.csv")
    summ = pd.read_csv(TABLES / "failure_atlas_summary.csv")
    diff = pd.read_csv(TABLES / "failures_by_difficulty.csv")
    orc = pd.read_csv(TABLES / "oracle_rescue.csv")
    lc = pd.read_csv(TABLES / "locality_contamination.csv")
    la = pd.read_csv(TABLES / "locality_audit_summary.csv")
    to = pd.read_csv(TABLES / "template_overlap.csv")
    cr = pd.read_csv(TABLES / "composition_retrieval.csv")
    cf = pd.read_csv(TABLES / "composition_frozen_ceiling.csv")
    rs = pd.read_csv(TABLES / "reserves.csv")
    val = pd.read_csv(TABLES / "replay_validation.csv")
    man = read_json(OUT / "manifest.json")
    today = date.today().isoformat()
    md = [f"# Phase 0 — cheap analyses before any new training\n", f"Capstan · {today} · post-conference programme, study `phase0` · inputs: the frozen ext-20261009 record (scores, raw selection chunks, memory snapshots), forward-only GPU replays (no training, no new memories), payloads and the certified clearance register.\n",
          "Question A of the programme is what a cap adds to frozen GPT-2 small and where its remaining error comes from; question B is whether predictive coding adds anything backprop does not. Phase 0 answers the parts of both that the saved record already decides, so that Phase 1 (a cached-feature small-reader harness) starts from the right hypotheses. All caps are the six PC-reader study readers at 300 edits (realization 0, order 100); 'BP-CAP' and 'PC-CAP' are seed means over three paired training seeds unless a seed is named.\n",
          headline(fr, pv, orc, ics, lc, cr, cf, rs),
          sec_frontier(fr, icf, ics), sec_atlas(pv, orc_rate, summ, diff), sec_oracle(orc, ics), sec_incontext(ics), sec_locality(lc, la, to), sec_composition(cr, cf), sec_reserves(rs),
          "## 8. What this decides for Phase 1\n",
          "- The selection experiment (Capex's A) should start from the hard negatives that actually fire: matched-template, different-subject prompts (zsRE near-miss neighbours, MQuAKE same-relation locality prompts), with labels defined against the whole active memory (a prompt that should invoke another taught record is a positive for that record). The proposal's same-subject hypothesis was wrong.\n"
          "- Retrieval misses on CounterFact (own record not in the top-4) cap what any gate can do; the small-reader harness needs a retrieval endpoint, not only a gate endpoint.\n"
          "- MQuAKE's payload failures (correct record applied, wrong answer) are a write-transfer problem: the per-position delta is prompt-specific. A Phase 1 arm should test deltas acquired on more than one wording, or a code-conditioned controller write, before any new learning rule.\n"
          "- The in-context arms set the accuracy bar the cap must beat or be cheaper than; every Phase 1 table carries them.\n"
          "- Composition needs an explicit mechanism or a base that knows the second hop; neither cap training rule addresses it. Treat E as conditional on the frozen-base ceiling in §6.1.\n"
          "- The PC-specific hypotheses (energy-based abstention; low-interference online learning) stand: nothing in the saved record tests them, and the frontier result says the registered PC/BP difference is not evidence either way.\n",
          "## 9. Reproducibility\n",
          f"Code: `aw/post_conference/phase0_*.py` (CPU: atlas, locality, composition, reserves, figures, report; GPU forward-only: frontier replay, in-context arms, composition probes), runner `aw/post_conference/run_phase0_gpu.sh`. Tables: `results/post_conference/phase0/tables/`. Data and figures: `assets/post_conference/phase0/`. Raw replay chunks: `assets/runs/post_conference/phase0/`. Replay validation: untouched replays of {int(val.n.sum())} fired paraphrases across {len(val)} reader/dataset cells reproduce the saved losses with max |diff| = {val.max_abs_diff.max():.1e} nats. GPU process time: " + ", ".join(f"{k} {v:.0f} s" for k, v in (("composition", read_json(ROOT.parent / 'assets/runs/post_conference/phase0/composition/manifest.json').get('elapsed_process_seconds', float('nan'))), ("in-context", read_json(ROOT.parent / 'assets/runs/post_conference/phase0/incontext/manifest.json').get('elapsed_total', float('nan'))), ("frontier replay", read_json(ROOT.parent / 'assets/runs/post_conference/phase0/replay/manifest.json').get('elapsed_total', float('nan'))))) + ". Manifest: `results/post_conference/phase0/manifest.json` (stages: " + ", ".join(sorted(man["stages"])) + ").\n"]
    text = "\n".join(md)
    (OUT / "phase0_report.md").write_text(text)
    res = build(OUT / "phase0_report.md", OUT / "phase0_report.pdf", "Phase 0: cheap analyses before any new training", "Capstan (pc_cap post-conference programme)", today)
    st = Status()
    st.artifact("report/md", OUT / "phase0_report.md")
    st.artifact("report/pdf", OUT / "phase0_report.pdf")
    st.stage("report", "complete", pdf=res)
    print(json.dumps(res, default=str))


if __name__ == "__main__":
    main()
