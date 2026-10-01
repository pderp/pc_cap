"""One-time PRES-7 document update, retained for review; no experimental calls."""
import json
from pathlib import Path
from aw.presentation_claims import read_rows, render_rows

root = Path.cwd()
deck = root / 'docs/presentation/deck_v3'
def slide(n, title, onscreen, paragraphs, sources):
    p = next(deck.glob(f'slide{n:02d}-*.md'))
    p.write_text(f'# Slide {n} — {title}\n\n**Draft speaker text for charlie\'s review; updated October 1, 2026.**\n\n'
                 f'**On screen:** {onscreen}\n\n## Speaker text\n\n' + '\n\n'.join(f'“{text}” [{claims}]' for text, claims in paragraphs)
                 + '\n\n## Sources and backup\n\n' + sources + '\n')
slide(6, 'How often, and how severe?',
      'HT-17 frequency versus conditional severity; both datasets, own-cap-off reference. The survival curves are backup.', [
('An average can conceal a small number of large unintended changes. We measure delta NLL: the increase in negative log probability of the actual next token when the cap is enabled at the same prefix. One nat means that token becomes a factor of e less probable. This is a prediction-loss measure, not human harm or the preference term of expected free energy.', '`HT-readout`'),
('The horizontal axis asks how often the increase exceeds 0.01 nat. Its denominator includes every scored position, including improvements and unchanged predictions. The vertical axis asks how large the increase is, on average, among positions exceeding that threshold. Neither axis is the gate firing rate: an activated correction need not cause harmful change.', '`HT17-tails`'),
('On zsRE, learned v5 has harmful changes at 0.1594 percent of positions with conditional severity 1.630 nats. Stable v0 has 0.1041 percent and 1.716 nats. On CounterFact, learned v5 has 0.2984 percent and 1.913 nats; the random reader has 2.0450 percent and 3.486 nats. Stable v0 has no observed harmful changes there, but also zero paraphrase retention. Its conditional severity is undefined, not zero.', '`HT17-tails`'),
('These are fifteen cells per condition and dataset: three subject realizations and five dependent orders, at a thousand edits. Every cell reuses the same 245,237 ordinary-text positions. The intervals resample matching window identities jointly, conditional on the observed cells. They do not account for subject or seed uncertainty, and independence between windows is unverified.', '`HT17-tails`'),
('Expected shortfall asks another question: ES99 averages positive loss within the worst one percent of all positions, with zeros and a fractional boundary retained. The maximum is the single largest observed event. Learned v5 on zsRE has a lower maximum than stable v0, 11.05 versus 27.68 nats, but a higher average cell ES99, 0.260 versus 0.179. No single summary orders every kind of risk.', '`HT17-tails`, `HT-readout`')],
'[HT-17 report](../../additional_work/HT-17_report.md); source snapshot `logs/additional_work/HT-17/snapshot-20261001-v2/report.json`.\n\nFigure: `assets/presentation-materials/figures/tails_ht17/round57/frequency-severity-stage4.png`. The original six-panel frequency/severity figure, including AW-B and partial reader seeds, remains backup. These replace the HT-13 main-screen slots; the earlier 270-cell empirical report remains valid at its stated scope.')
slide(7, 'What does the observed tail shape add?',
      'Three qualified findings: learned v5, stable v0 on zsRE, and invalid or sparse fits. Intervals are conditional window-bootstrap intervals.', [
('We fitted the positive excess above each threshold with a generalized Pareto distribution and compared it with the exponential special case. This is the one-sided alpha-equals-one family discussed in Nelson’s manuscript. Shape and scale are fitted separately; scale depends on the threshold. At least a hundred excesses in thirty windows were required. This is an exploratory finite-range model comparison.', '`HT17-tails`'),
('For learned v5, shape estimates at 0.01 nat are close to zero: 0.0435 to 0.0588 on zsRE and 0.0294 to 0.0978 on CounterFact. The fixed illustrative realization-zero, order-one-hundred intervals are minus 0.097 to 0.177 and minus 0.009 to 0.187. Both include zero. Held-out-window log-likelihood gains over the exponential are tiny, at most about 0.0028 nats per excess. An exponential is an economical approximation on this measured range; this is not an equivalence test.', '`HT17-tails`'),
('Stable v0 on zsRE shows a more pronounced tail: fitted shapes range from 0.433 to 1.029, with an illustrative interval of 0.390 to 0.779. Held-out predictive gains are 0.149 to 0.594 nats per excess in every cell. But at a one-nat threshold, thirteen of fifteen cells have too few events for a fit. The evidence does not establish the farthest tail or infinite variance.', '`HT17-tails`'),
('The random CounterFact reader illustrates a failure mode: all fitted shapes are negative, yet ten of fifteen held-out comparisons fail because an estimated endpoint excludes an observed held-out event. Every mixture fit has an endpoint pathology and is labelled invalid. Sparse random-zsRE, stable-CounterFact and individual kappa-pilot cells have no eligible headline shape. These cases remain in the report.', '`HT17-tails`'),
('We have not measured system state growth, identified a complexity class or assigned a temperature. The scientific advance is a tested distinction in the observed shape of prediction-loss changes, with failed predictions visible. Those consequences can inform a future active-inference audit policy; they do not establish one.', '`HT17-tails`, `AI-next`')],
'[HT-17 methods and all cells](../../../logs/additional_work/HT-17/snapshot-20261001-v2/report.md). [Tail backup](backup-ht17.md) contains the survival figure and precise predictive-score ranges. Outcome-independent illustrative choice: realization 0, order 100. No interval covers training-seed or subject-population uncertainty.')
# Keep slide 8 measured proof/cost paragraphs and add the new, distinct inference.
p = deck / 'slide08-kappa-tradeoff.md'
s = p.read_text()
a = s.index('“The kappa pilot')
b = s.index('\n\n', a)
s = s[:a] + '“The kappa pilot replaced one answer surprisal ℓ with the bounded loss (1 − exp(−κℓ))/κ, saturating at 1/κ. The tested settings, 0.2 and 0.5, failed the declared retention and tail-separation rule; ordinary clipping also reduced the tail. This uses the coupled-logarithm family, but differs from Nelson’s calibrated entropy in its probability transformation, independent-equals or escort averaging, outer root and informational-scale calibration. We did not test that entropy or a coupled free-energy objective. This result neither confirms nor refutes those untested proposals.” [`kappa-design`]' + s[b:]
s = s.replace('## Sources and backup', '“HT-17 separates the mixture’s effect into frequency and severity. Frequency above 0.01 nat is almost unchanged, while conditional severity falls from 1.619 to 0.542 nats on zsRE and 1.925 to 0.581 on CounterFact. All ten generalized-Pareto mixture fits hit an endpoint pathology and are invalid; none yields a tail-class estimate. The one-nat ceiling follows from the mixture algebra, independently of those fits.” [`AW-B`, `HT17-tails`]\n\n## Sources and backup')
p.write_text(s)
p = deck / 'slide02-active-inference-testbed.md'
s = p.read_text().replace('or a coupled free-energy formulation.”', 'or a coupled free-energy formulation. Nelson’s manuscript offers a candidate objective; a matching probability model and constraints remain to be specified.”').replace('[`AI-loop`, `AI-programme`]\n\n“This gives', '[`AI-loop`, `AI-programme`, `AI-coupled-FE`]\n\n“This gives')
p.write_text(s)
slide(11, 'Return to active inference: what should the agent do next?',
      'Implemented correction and measured consequences beside a proposed policy loop. Coupled free energy remains a candidate objective, not an implemented result.', [
('Active inference asks what the agent should do next. Our cap acquires corrections, and our assays measure their benefits and unintended consequences. A future controller might probe a paraphrase, audit unrelated text, request an observation or leave memory unchanged. We would need hidden-state beliefs, observation and action models, preferences and expected information to compare those policies.', '`AI-next`, `AI-programme`'),
('Nelson’s coupled-entropy framework and the proposed coupled free energy are candidates for that objective. With their authors, we first need to specify the probability model, constraints, escort weighting, gradients and policy loop. A bounded transformation of one training loss supplies none of those specifications by itself. The architectural interfaces also do not prove Markov-blanket conditional independence.', '`AI-coupled-FE`, `kappa-design`'),
('The predictive-coding experiments now measure learning-credit trade-offs in retention, unintended loss and cost. The tail analysis separates frequency from severity and checks which finite-range models predict held-out events. The mixture supplies a proven per-token ceiling with a measured efficacy cost. These are useful components and measurements for designing an audit policy.', '`PC-v0`, `PC-fixed-v5`, `HT17-tails`, `AW-B`'),
('We have not demonstrated autonomous epistemic action: investigators still choose the observations and tests. A next experiment could compare policy-guided audits against fixed or random audits under the same budget, measuring useful corrections, information, loss and cost. That is a proposed study after this programme, not another commitment before October 9.', '`AI-next`, `AI-coupled-FE`')],
'[Abstract-to-testbed map](../abstract_to_testbed.md), [feedback and conservative B–D text](../../friday-10.02-review/talk-text-B-C-D.md), [HT-17 report](../../additional_work/HT-17_report.md). The κ pilot neither confirms nor refutes the untested calibrated entropy, coupled free energy or one-κ conjecture.')
# Ledger updates preserve every unrelated row.
p = root / 'docs/talk_claim_ledger_v7.md'
s = p.read_text(); rows = read_rows(s)
for row in rows:
    if row[0] == 'kappa-design':
        row[3] = 'Bounded loss (1-exp(-κℓ))/κ, κ=.2/.5; saturation 1/κ; both fail retention floor .776111 and declared tail separation'
        row[7] += '; not Nelson calibrated entropy: different probability transform, no independent-equals/escort averaging, outer root or informational-scale calibration; neither confirms nor refutes the untested objective'
    if row[0] == 'AW-B':
        row[3] += '; HT-17 conditional severity zsRE 1.619→.542 and CF 1.925→.581 nats, frequency nearly unchanged'
        row[7] += '; all ten mixture GPD fits invalid at endpoint, no published shape; analytic ceiling independent of fit'
        row[8] += '; docs/additional_work/HT-17_report.md'
new = [
['HT17-tails','Heavy-tailed distributions / extremes','exploratory measured','Learned near-zero shapes with little held-out gain; stable-zsRE shapes .433–1.029, gain .149–.594 nats/excess; random-CF 10/15 support failures','299 cells incl 90 primary Stage-4; threshold .01 plus .1/.5/1; 4 reader evaluations pending','Own cap-off, same window identities; exponential vs GPD; >=100 excesses and >=30 windows','Separate harmful-change frequency and conditional severity; finite-range shape differences; invalid/sparse fits retained','No complexity class, W(N), temperature, infinite variance or asymptotic law; conditional window intervals exclude realization/seed uncertainty and assume unverified window independence','docs/additional_work/HT-17_report.md; logs/additional_work/HT-17/snapshot-20261001-v2/report.json'],
['AI-coupled-FE','Active inference','proposed','Nelson 2026 coupled-entropy framework as candidate objective; specify probability model, constraints, escort weighting, gradients and policy loop','Future jointly specified experiment','No implemented coupled-objective comparison','A concrete next specification linking learning, consequences and audit choice','Not implemented by the κ pilot or two software interfaces; no coupled blanket, autonomous policy or one-κ finding','docs/friday-10.02-review/talk-text-B-C-D.md; docs/friday-10.02-review/feedback-MMK-nelson-entropy-capex.md']]
rows = [r for r in rows if r[0] not in {x[0] for x in new}] + new
p.write_text(s.split('| ID |',1)[0] + render_rows(rows))
# Short, wide figure on slide6; three qualified findings on slide7.
p = deck/'diagram-specs.json'; specs = json.loads(p.read_text())
for s in specs['slides']:
    if s['number']=='01': s['panels'][1]['lines'][2]='MEASURED TRADE-OFFS'
    if s['number']=='02': s['claims'].append('AI-coupled-FE'); s['notes']='Interfaces are implemented. Coupled objective, blanket properties and policy loop remain proposed.'
    if s['number']=='06':
        s.update(title='How often, and how severe?',status='HT-17: Stage-4 primary conditions; 1,000 edits; fixed ordinary-text inventory',claims=['HT17-tails','HT-readout'],figure='assets/presentation-materials/figures/tails_ht17/round57/frequency-severity-stage4.png',figure_manifest='assets/presentation-materials/figures/tails_ht17/round57/manifest.json',requires_tail_gate=False,footer='Frequency above 0.01 nat is not gate firing. Severity is conditional on exceeding that threshold.',notes='Same positions reused; window intervals do not cover subject or seed uncertainty.')
    if s['number']=='07':
        s.pop('figure',None); s.pop('requires_tail_gate',None)
        s.update(title='What does observed tail shape add?',status='Exploratory finite-range fits; primary threshold 0.01 nat',claims=['HT17-tails'],connections=False,panels=[
            dict(title='Learned v5',lines=['Illustrative 95% shape intervals','zsRE: -0.097 to 0.177','CF: -0.009 to 0.187']),
            dict(title='Stable v0 · zsRE',lines=['Illustrative interval: .390–.779','Held-out gain: .149–.594','nats/excess across 15 cells']),
            dict(title='Limits remain visible',lines=['Random CF: 10/15 failures','Mixture: all fits invalid','Sparse cells: no shape'])],footer='Learned v5: little predictive gain over exponential. Stable v0: a more pronounced observed tail.',notes='Conditional window intervals; illustrative r0/order100. No asymptotic class or infinite-variance finding.')
    if s['number']=='08': s['claims'].append('HT17-tails'); s['notes']='κ pilot: bounded surprisal, not calibrated entropy. Mixture: analytic one-nat ceiling at shared prefix.'
    if s['number']=='11':
        s['claims']=['AI-programme','AI-next','AI-coupled-FE','HT17-tails','PC-v0','PC-fixed-v5']
        s['panels'][1]['lines']=['Probability model + constraints','Preferences + escort weighting','Gradients + action model']
        s['notes']='Coupled free energy is a candidate objective. No implemented policy loop or blanket theorem.'
p.write_text(json.dumps(specs,indent=2)+'\n')
(deck/'backup-ht17.md').write_text('''# HT-17 backup — measured results supersede the prototype appendix

Draft for charlie, October 1. Source: [HT-17 report](../../additional_work/HT-17_report.md).
The prototype appendix in the B–D drafting document is historical; use these results.

Survival/threshold figure: `assets/presentation-materials/figures/tails_ht17/snapshot-20261001-v2/survival_thresholds.png` (PDF/SVG beside it). Fixed illustrative r0/order100; every cell remains in the source tables.

- Learned v5 shape ranges: zsRE .0435–.0588; CF .0294–.0978. Illustrative 95% intervals: [-.097,.177], [-.009,.187]. Held-out GPD−exponential gains across all fifteen cells: zsRE -.000394 to +.000259; CF -.001041 to +.002765 nats/excess. No equivalence claim.
- Stable v0 zsRE: shapes .433–1.029; illustrative interval [.390,.779]; predictive gains .149–.594. At threshold 1 nat, 13/15 cells fail the sample screen.
- Random CF: negative shapes, but 10/15 predictive comparisons invalid due to held-out support failures. The other five gain about .033 nats/excess. Not a guaranteed bound.
- Random zsRE, stable CF and all individual κ-pilot cells: insufficient events/windows. Undefined conditional severity stays undefined.
- AW-B: severity 1.619→.542 (zsRE), 1.925→.581 (CF), near-unchanged frequency. Paired differences: [-1.197,-.979] and [-1.456,-1.251] nats. All ten GPD fits invalid at endpoint; analytic mixture ceiling remains valid.
- Reader seeds: only seed0 paired so far. CF ePC−BP severity -.232, interval [-.527,+.089]; frequency lower. zsRE ePC has no events above .01. Other seeds pending, no superiority claim.

All intervals condition on observed cells, with unverified window independence. No system-state growth W(N), temperature, asymptotic tail class or infinite variance was measured. HT-17 uses a generalized Pareto with fitted shape and scale, not a free-α entropy fit.
''')
p = root/'docs/presentation/final-experiments.md'; s=p.read_text().replace('DEC-077/078 decisions','DEC-077/078/080/081/081a decisions').replace('4 cells complete, 1 ceiling-exhausted, 25 pending. R-2 reconciliation complete; explicit v0 class deferral recommended pending a versioned batching repair.','4 cells complete, 1 ceiling-exhausted and incomplete, 16 learned/random cells pending; 9 remaining v0 cells explicitly deferred under DEC-080. R-2 reconciliation complete; no higher ceilings.')
s=s.replace('## Conditional branches from the primer','''## Feedback and tail-analysis update — DEC-081/081a

Approved B–D wording distinguishes the bounded κ-surprisal pilot from the untested calibrated coupled entropy. HT-17 now reports 299 cells, including all available reader seeds; four ePC evaluations await completion. It separates harmful-change frequency and conditional severity, reports finite-range fits and held-out failures, and preserves the analytic mixture bound independently of invalid fits. No complexity classes, W(N), temperature or infinite variance were measured. See `docs/additional_work/HT-17_report.md` and deck slides 2/6/7/8/11.

The remaining GPU portfolio is unchanged; no coupled-objective model fit or free-α sweep is added. Option R resumes learned/random only under DEC-080. October 9 at 17:00 EDT remains the experimental cutoff; no new model fits start on or after October 6.

## Conditional branches from the primer''')
p.write_text(s)
p=root/'docs/presentation/review-results.md'; s=p.read_text(); s += '''

## HT-17 — frequency, severity and finite-range shape (October 1)

The [HT-17 report](../additional_work/HT-17_report.md) supersedes the prototype tail appendix. Across 299 cells it separates frequency above .01 nat from mean severity conditional on exceeding it. Primary learned-v5 frequencies/severities are .1594%/1.630 nats on zsRE and .2984%/1.913 nats on CounterFact. Stable v0 has a more pronounced fitted zsRE tail, yet its maximum and ES99 order differently against v5; zero CF harm accompanies zero paraphrase retention.

Learned-v5 illustrative shape intervals include zero, with little held-out predictive gain over exponential. Stable-zsRE GPD gains .149–.594 nats per excess, with illustrative shape interval [.390,.779]. Random CF has 10/15 held-out support failures; all mixture fits are invalid. These are finite-range observations, not complexity classes or infinite-variance measurements. Conditional window intervals omit realization/seed uncertainty, and window independence remains unverified.

AW-B reduces conditional severity 1.619→.542 and 1.925→.581 nats, with almost unchanged harmful-change frequency. Its one-nat shared-prefix ceiling is analytic, independent of failed tail fits. The κ pilot deformed one surprisal; it did not implement Nelson’s calibrated entropy or coupled free energy. The active-inference policy loop remains proposed.

DEC-080 defers nine unrun Option R stable-v0 cells; the earlier ceiling-killed cell remains incomplete. Sixteen learned/random cells await resumption. DEC-081/081a adds CPU analysis and conservative presentation wording, not another GPU experiment. PC-reader replication remains partial (three BP seeds, one ePC seed); no three-seed rule comparison is yet available.
'''; p.write_text(s)
