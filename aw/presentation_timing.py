"""PRES-5 timed speaking drafts from the existing twelve-slide claim set."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/presentation/deck_v3"

SHORT = [
    """Our question is how a small adaptive system on a frozen language model could learn useful corrections while remaining attentive to their unintended consequences. That connects the three themes of this session: active inference, predictive coding, and heavy-tailed distributions.

Active inference asks what to do next. Predictive coding gives us a question about how to learn a correction. The study of extremes asks whether a few predictions can become much worse even when the average change is small. I will distinguish the proposed agent from the components and measurements we have tested.""",
    """On the right of this diagram is a pretrained transformer. In the main condition its weights stay fixed, supplying predictions and representations. In the middle is the adaptive cap: it stores corrections, decides when a memory applies, and supplies bounded changes to internal representations. A null decision lets it leave the original prediction alone.

On the left are the edits and evaluation questions supplied by us. That is the boundary of the present experiment. The system does not yet choose its own audit by comparing expected information and preferred outcomes. The dashed return loop represents that proposed extension.

This architecture gives us a testbed for two questions: which learning signal makes a useful correction, and what else does the correction change? The software interfaces do not themselves establish a Markov blanket or coupled free energy.""",
    """To teach a correction, we need a direction for changing its stored residual write. SE-A obtains that direction from the answer-loss derivative, the ordinary adjoint calculation. SE-E introduces temporary error variables and lets them settle, then uses their values at the write sites as acquisition credit. The same base and bounded update policy surround the two alternatives.

The settling energy is a quadratic penalty on the inference errors plus the taught-answer loss. We hold the existing write fixed, initialize errors at zero, and take eight steps at learning rate one tenth. The teaching target is supplied for acquisition, not during evaluation.

An earlier implementation penalized the error plus the write, where the intended penalty was on the error alone. SD-24 corrected that defect. The older SE-E result remains a separate historical reference; the completed R1 feedforward experiment did not use this PC path.

The actual solver passes the one-step check against the negative adjoint even with nonzero writes. That check does not prove that longer settling helps. This implementation uses JAX differentiation and nine forward/reverse evaluations for eight steps, so the experiment concerns predictive-coding acquisition credit; wholly backpropagation-free computation and biological locality are not established.""",
    """Here is the correction testbed in one pass: teach a fact, ask it again, ask its paraphrase after further edits, and check unrelated predictions. Immediate success, retained paraphrase success and locality measure different properties.

The base and previously BP-trained reader are fixed; memory changes during the stream. We compare declared packages, with three realizations and five dependent orders per realization. The orders reuse subjects, so they are not extra independent populations.""",
    """The learned reader's final paraphrase retention averages about 96 percent on zsRE and 68 percent on CounterFact after a thousand edits. The points show the individual realizations. MQuAKE reaches about 72 percent at its separate three-hundred-edit endpoint.

Three of four available triplet contrasts receive a preliminary positive label. CounterFact versus the stable cap remains inconclusive because locality drops to 48 of 50 prompts in realization two.

On zsRE, all fifty locality answers are preserved, yet only 86, 92 and 87 of a hundred near misses are preserved across realizations. Useful retention therefore coexists with specificity failures. These limited three-cluster summaries describe the tested populations; they do not establish population-wide superiority.""",
    """The curve asks how often a prediction's loss increase exceeds a chosen threshold. Positive delta NLL means less probability for the actual next token when the cap is enabled. One nat means a factor-of-e reduction in that probability. This is prediction loss, not a direct measure of human harm.

Moving right asks about greater severity; moving down asks about greater rarity. Zero changes remain in the denominator even though zero cannot appear on the logarithmic axis.

Expected shortfall, ES99, averages positive loss within the worst one percent of all positions, retaining zeros and a fractional boundary. It is different from the percentile threshold. We use it alongside frequency, maxima and concentration to see what a mean conceals.""",
    """For zsRE, the learned reader and live-C2 comparator have small mean signed loss increases, about two-and-a-half and three-point-two thousandths of a nat. Their maxima are about 11 and 51 nats. The learned reader affects more positions at the displayed threshold; live C2 has a rarer but more severe observed extreme.

All forty-five learned-reader cells exceed the secondary mean-KL benchmark. That is a preservation finding, separate from data integrity. The reference here is each condition's own cap-off base.

These are finite empirical distributions with repeated positions across cells. Neither a power law nor an asymptotic heavy-tail family is established, and the figure does not demonstrate robustness to unseen extreme regimes.""",
    """The kappa pilot asks whether changing the reader's training loss can reduce unintended tail loss. Both kappa settings reduced a development tail statistic, but lost too much retention and failed the declared retention and tail-separation rule. Clipping also reduced the tail descriptively.

We therefore retain this as a preliminary trade-off, without a declared gain. Changing that loss did not implement coupled free energy, a coupled Markov blanket or a test of the one-kappa conjecture.""",
    """Now the corrected PC comparison: the same frozen v0 cap and regenerated ePC base, changing only acquisition credit. We reuse exposed historical S5 streams, with three realizations and five dependent orders, ending at a thousand edits for zsRE and three hundred for CounterFact. This is a supplemental defect-correction replication.

SE-E minus SE-A in paraphrase retention is {{v0.zsre.ret_gs}} on zsRE and {{v0.counterfact.ret_gs}} on CounterFact. The three realization differences are {{v0.zsre.ret_gs.realizations}} and {{v0.counterfact.ret_gs.realizations}}. Locality differences are {{v0.zsre.ls}} and {{v0.counterfact.ls}}. Higher favors SE-E for behavior.

The difference of arm ES99 positive-harm values is {{v0.zsre.harm_es99_difference}} and {{v0.counterfact.harm_es99_difference}} nats on the matched ordinary-text positions. Lower favors SE-E here. These are differences of tail summaries, not the tail of positionwise differences.

Process time is {{v0.SE-A.seconds}} seconds for SE-A and {{v0.SE-E.seconds}} for SE-E, plus {{v0.harm.seconds}} for the separate readout. The cost includes acquisition and evaluation. We need all three: behavior, harm and cost, including an adverse or null result.""",
    """The transfer check keeps the selected BP-trained v5 reader and original base fixed. The reader is not retrained with predictive coding. Both arms begin with fresh memory; acquisition credit changes.

This is a small post hoc comparison: exposed realization zero, one order, three hundred edits on each dataset. At that endpoint the SE-E minus SE-A paraphrase-retention differences are {{v1.zsre.ret_gs}} and {{v1.counterfact.ret_gs}}. Near-miss differences are {{v1.zsre.near_miss}} and {{v1.counterfact.near_miss}}, and semantic revision differences are {{v1.zsre.revision}} and {{v1.counterfact.revision}}.

The ES99 harm differences are {{v1.zsre.harm_es99_difference}} and {{v1.counterfact.harm_es99_difference}} nats. This readout uses the same full ordinary-text positions for both arms, not independent token replicates. Stream-engine times are {{v1.SE-A.seconds}} and {{v1.SE-E.seconds}} seconds, plus {{v1.harm.seconds}} for harm. These results test credit transfer on this reader; they do not establish a complete active-inference agent.""",
    """Return to active inference: what should the agent do next? A future controller might audit a nearby paraphrase, probe unrelated text, request another observation, or leave memory unchanged. To compare those policies through expected free energy, we would need beliefs about hidden states, an observation and action model, preferences and expected information.

The PC experiment tests a learning mechanism. The tail measurements reveal consequences that an audit policy might need to detect. Neither automatically supplies autonomous epistemic action; currently we, the investigators, choose the probes and learn from the failures.

A useful next study would compare policy-driven and fixed or random audits with equal budgets, measuring corrections, information, preservation and cost. That is a proposed scientific comparison, not another experimental promise before October 9.""",
    """The three themes leave us with three questions sharpened by evidence. Active inference supplies the proposed belief-and-action loop. Predictive coding has a direct paired mechanism test, whose retention differences are {{v0.zsre.ret_gs}} and {{v0.counterfact.ret_gs}} on the historical streams. Empirical extremes show why a small average is insufficient to describe unintended consequences.

The main run stopped at the approved 270-cell scope, with omitted comparisons reported as unavailable. Experiments finish October 9 at 17:00 Eastern; analysis, slides and rehearsal follow before October 15. I welcome discussion about the next controlled test of informative audits.""",
]

CHOICES = {1:[0,1], 2:[0,1,2], 3:[0,1,2,4], 4:[0,1,4], 5:[0,2,4,5],
           6:[1,2,4,5], 7:[1,3], 8:[0,2,4], 9:list(range(5)), 10:list(range(5)),
           11:[0,1,5], 12:[0,1,2,4]}
BUDGETS = {15:[50,85,125,35,75,70,65,40,115,100,85,55],
           25:[65,120,165,110,115,150,80,100,170,170,120,135]}


def stamp(seconds):
    return f"{seconds//60:02d}:{seconds%60:02d}"


def main():
    originals = sorted(SOURCE.glob("slide*.md"))
    evidence, long = {}, []
    for n, p in enumerate(originals, 1):
        full = p.read_text()
        body = full.split("## Speaker text\n", 1)[1].split("\n## ", 1)[0]
        paragraphs = re.findall(r'“(.*?)”', body, re.S)
        long.append("\n\n".join(paragraphs[i].replace("“", "") for i in CHOICES[n]))
        evidence[p.name] = dict(sha256=hashlib.sha256(full.encode()).hexdigest(),
                               claims=sorted(set(re.findall(r'`([A-Za-z0-9-]+)`', body))))
    records = {}
    for minutes, texts in ((15,SHORT),(25,long)):
        budgets = BUDGETS[minutes]
        assert sum(budgets) == minutes*60
        records[str(minutes)] = []
        rows, t = [], 0
        for n, (words, seconds) in enumerate(zip(texts,budgets),1):
            # Replace slot tokens by a representative three-word spoken number;
            # realization lists expand further when the actual report is available.
            counted = re.sub(r'\{\{[^}]+\}\}', 'pending measured value', words)
            counted = re.sub(r'\\\[.*?\\\]', '', counted, flags=re.S)
            count = len(counted.split())
            records[str(minutes)].append(dict(slide=n, start_seconds=t, seconds=seconds,
                                              approximate_words=count, implied_words_per_minute=60*count/seconds))
            rows.append(f"| {n} | {stamp(t)}–{stamp(t+seconds)} | {seconds} s | {count} |")
            t += seconds
        text = f"""# {minutes}-minute speaking script — draft for charlie

Prepared 2026-09-27 by Capex from the twelve slide drafts. **Author review and
rehearsal required; this is a duration option, not a confirmed conference slot.**
Clock includes slide changes and pointing pauses, excludes audience Q&A. Read
only the paragraphs under “Say”; source/cut notes and tables are not spoken.

PC values remain literal result slots. After complete reports exist, the existing
presentation export resolves them from `pc-result-sources.json`; an absent source
renders PENDING, never zero. If still pending at rehearsal, say “this comparison
is pending; I cannot yet report a direction or effect” instead of the numerical
paragraph. Do not read placeholder braces aloud or imply completion prematurely.

Word counts approximate slot values as three spoken words and omit the displayed
equation. Rehearse again after filling actual numbers, particularly realization
lists; timing is a target, not a measured delivery duration.

| Slide | Running clock | Allocation | Approximate spoken words |
| --- | --- | --- | --- |
""" + "\n".join(rows) + f"\n\nTotal allocation: **{minutes}:00**.\n\n"
        if minutes == 15:
            text += """Short-version cuts follow the outline: slides 4–5 form one 1:50 unit
(35 seconds of design, then 75 of results); slides 6–7 form one 2:15 unit.
Keep both slide numbers for the existing figure files and advance at the stated
clock. The kappa section is 40 seconds; detailed settling diagnostics, operation
tables, comparator breakdowns and process accounting move to backup. Retain the
active-inference opening and return, corrected-PC comparison and empirical tails.

"""
        else:
            text += """This version retains separate design/results and distribution/consequence
slides. If the chair requests 15 minutes, use the companion script: merge 4–5
and 6–7 as speaking units, shorten kappa and move diagnostics/accounting to backup.
Do not obtain the shorter version by removing one of the three central themes.

"""
        for p, words, record in zip(originals,texts,records[str(minutes)]):
            title = p.read_text().splitlines()[0].removeprefix("# ")
            start = record["start_seconds"]
            text += f"## {title}\n\n**{stamp(start)}–{stamp(start+record['seconds'])}; {record['seconds']} seconds.**\n\n"
            text += "Say:\n\n" + words + "\n\n"
            text += "Evidence: " + ", ".join(f"`{x}`" for x in evidence[p.name]["claims"]) + f"; [source draft]({p.name}).\n\n"
        text += """## Cut and backup instructions — not spoken

- Slides 4–5: omit the control-by-control tour and detailed order/t-sensitivity tables;
  keep what changes, what stays fixed, independent realizations and the specificity limitation.
- Slides 6–7: show frequency and severity together; retain the reference label, repeated-position
  caveat and distinction between empirical concentration and an established heavy-tail family.
- Slide 3: the detailed one-step/nonzero-write diagnostic and full operation ledger are backup;
  retain SD-24's meaning and the JAX differentiation qualification.
- Slide 8: retain the failed decision rule and coupled-free-energy limitation even when short.
- Slides 9–10: full per-order metrics, 100-edit tables and cost breakdowns are backup; retain
  effect, harm, cost, exposed population and any unfavorable result.
- Slide 12: detailed process accounting is backup (392.42 process-hours for the main 270-cell
  snapshot, excluding separate PC work; overlapping workers prevent equating it to elapsed GPU time).
  Keep the October 9 experimental deadline and October 15 presentation distinct.

All claims use [claim ledger v7](../../talk_claim_ledger_v7.md). The ledger and
the completed result sources, rather than an inference from the story, determine
the final PC interpretation. No new experimental commitment is made by this script.
"""
        with (SOURCE / f"speaking-script-{minutes}min.md").open("x") as f:
            f.write(text)
    with (ROOT / "logs/additional_work/round50/presentation-timing.json").open("x") as f:
        json.dump(dict(source_drafts=evidence, timings=records),f,indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
