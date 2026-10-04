"""Support information: concrete per-item examples from the Stage-4 confirmatory cells (Capstan, 2026-10-04).

For each dataset (zsRE, CounterFact, MQuAKE), realization 0, order 100: the first N edits of the stream with the prompt,
the new target, the paraphrase, the frozen base's own greedy answer (computed here on CPU with the sealed Stage-4 base;
for CounterFact it equals the payload's stored ``teacher_generation``), and, for every condition that ran at that
coordinate, the answer generated right after the edit (ES), the answer at the end of the stream on the original prompt
(RET-ES) and on the paraphrase (RET-GS). Plus a few locality, near-miss, unseen-prompt and revision cases with the
cap-off reference answer beside each cap's answer. Everything is read from the sealed payloads and the cells' checkpoint
files; the only model execution is the base-only decode of the shown prompts (CPU, no cap, no writes).

    JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONPATH=src:. ../venv/bin/python -m aw.support_examples \
        --out /home/derp/cap/assets/support-information --n 30
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "results/R1/stage4_sealed_cells"
RECIPES = ROOT / "docs/tasks/R1-final-cell-recipes"
BASE = "/home/derp/cap/assets/runs/pc_cap/R1/stage4_dev_bases/c5b784c4e67a8eda5b79a4036be236a27642fe8f33baf8fc64d9229971ffb189"
FINAL = {"zsre": 1000, "counterfact": 1000, "mquake": 300}
LABEL = {
    "R1_learned_ff": "learned reader v5 (primary)",
    "R1_nonlearned": "random-geometry reader + gate (control)",
    "v0_stable": "stable v0 cap",
    "matched_update": "matched-update adapter",
    "v0_live_C1": "live v0 cap C1",
    "v0_live_C2": "live v0 cap C2",
    "S1_LM": "continued base (LM) + stable cap",
    "S1_literal": "continued base (literal) + stable cap",
}
ORDER = list(LABEL)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def payload_for(dataset: str) -> Path:
    for f in RECIPES.glob("*.json"):
        j = json.loads(f.read_bytes())
        c = j.get("cell", j)
        if c.get("dataset") == dataset and c.get("realization") == 0 and c.get("order") == 100 and c.get("condition") == "R1_learned_ff":
            def find(o):
                if isinstance(o, dict):
                    if isinstance(o.get("payload"), dict) and "path" in o["payload"]:
                        return o["payload"]["path"]
                    for v in o.values():
                        r = find(v)
                        if r:
                            return r
            return Path(find(j))
    raise FileNotFoundError(dataset)


def cells_for(dataset: str) -> dict[str, Path]:
    out = {}
    for d in CELLS.glob(f"*-{dataset}-0-100-*"):
        cond = d.name.split(f"-{dataset}-")[0]
        cp = d / "attempt-0000" / f"checkpoint-{FINAL[dataset]}.json"
        if cp.exists():
            out[cond] = cp
    return {k: out[k] for k in ORDER if k in out}


def short(s: str | None, n: int = 140) -> str:
    if s is None:
        return "—"
    s = s.replace("\n", "⏎")
    return s if len(s) <= n else s[: n - 1] + "…"


def tick(flag) -> str:
    return "✓" if flag else ("✗" if flag is not None else "·")


def base_decoder():
    import numpy as np

    from pccap.bases.bp import BPBase
    from pccap.data.decode import greedy_decode
    from pccap.data.tokenize import GPT2Tokenizer

    base, tok = BPBase(BASE), GPT2Tokenizer(Path(BASE))

    def predict(ids):
        return base.forward(np.asarray(ids, np.int32), phase="query", last_only=True).logits

    cache: dict[str, dict] = {}

    def answer(prompt: str) -> dict:
        if prompt not in cache:
            d = greedy_decode(predict, np.asarray(tok.encode(prompt), np.int32), tok, max_new=32)
            cache[prompt] = {"generated": d.text, "stopped_by": d.stopped_by}
        return cache[prompt]

    return answer


def build(dataset: str, n: int, answer, mode: str = "first", seed: int = 0, skip: int = 30) -> dict:
    payload = payload_for(dataset)
    pj = json.loads(payload.read_bytes())
    items = {it["item_id"]: it for it in pj["items"]}
    cells = cells_for(dataset)
    cps = {c: json.loads(p.read_bytes()) for c, p in cells.items()}
    primary = cps["R1_learned_ff"]
    full_order = [h["item_id"] for h in sorted(primary["history"], key=lambda h: h["index"])]
    if mode == "first":
        positions = list(range(n))
    else:
        import random

        positions = sorted(random.Random(seed).sample(range(skip, len(full_order)), n))
    order = [full_order[i] for i in positions]
    rows = []
    for k, iid in enumerate(order, 1):
        it = items[iid]
        para = (it.get("paraphrases") or [None])[0]
        row = dict(index=k, stream_position=positions[k - 1] + 1, item_id=iid, prompt=it["prompt"], target=it["answer"], aliases=it.get("aliases", []),
                   paraphrase=para, target_true=(it.get("target_true", {}).get("str") if isinstance(it.get("target_true"), dict) else it.get("target_true")),
                   base_prompt=answer(it["prompt"]), base_paraphrase=(answer(para) if para else None),
                   stored_teacher_generation=it.get("teacher_generation"), conditions={})
        for c, cp in cps.items():
            h = next((x for x in cp["history"] if x["item_id"] == iid), None)
            r = next((x for x in cp["retention"]["rows"] if x["item_id"] == iid), None)
            row["conditions"][c] = dict(
                immediate=(dict(generated=h["query"]["generated"], es=h["es"], outcome=h["outcome"]["code"]) if h else None),
                final_prompt=(dict(generated=r["query"]["generated"], es=r["es"]) if r else None),
                final_paraphrase=(dict(generated=r["paraphrases"][0]["generated"], exact=r["paraphrases"][0]["exact"],
                                       fired=not r["paraphrases"][0]["selection"]["hard_null"] if r["paraphrases"][0].get("selection") else None) if r and r.get("paraphrases") else None),
            )
        rows.append(row)
    # endpoint examples
    ep = pj["endpoints"]
    loc_rows = {r["item_id"]: r for r in ep["locality"]["rows"]}
    nm_rows = {r["item_id"]: r for r in ep["near_miss"]["rows"]}
    rev_rows = {r["item_id"]: r for r in ep["revision"]["rows"]}
    uns_rows = {r["item_id"]: r for r in ep["unseen"]["rows"]}

    def per_condition(section, idx, pick):
        out = {}
        for c, cp in cps.items():
            rs = (cp.get(section) or cp["endpoints"].get(section) or {}).get("rows") or []
            out[c] = pick(rs[idx]) if idx < len(rs) else None
        return out

    locality = []
    for i in range(5):
        r0 = primary["locality"]["rows"][i]
        locality.append(dict(item_id=r0["item_id"], prompt=loc_rows[r0["item_id"]]["prompt"],
                             conditions=per_condition("locality", i, lambda r: dict(cap=r["query"]["generated"], reference=r["reference"]["generated"], preserved=r["preserved"]))))
    near = []
    for i in range(5):
        r0 = primary["endpoints"]["near_miss"]["rows"][i]
        src = nm_rows[r0["item_id"]]
        near.append(dict(item_id=r0["item_id"], edit_prompt=src["edit_prompt"], edit_answer=src["edit_answer"],
                         neighbour_prompt=src["neighbour_prompt"], neighbour_answer=src["neighbour_answer"],
                         conditions=per_condition("near_miss", i, lambda r: dict(edited=r["edited_query"]["generated"], edit_exact=r["edit_exact"],
                                                                                 neighbour_cap=r["neighbour_query"]["generated"], neighbour_reference=r["reference"]["generated"], preserved=r["preserved"]))))
    unseen = []
    for i in range(3):
        r0 = primary["unseen"]["rows"][i]
        src = uns_rows.get(r0.get("item_id"), {})
        unseen.append(dict(item_id=r0.get("item_id"), prompt=src.get("prompt"), stored_answer=src.get("answer"),
                           conditions=per_condition("unseen", i, lambda r: dict(cap=r["cap_query"]["generated"], changed=r["answer_changed"]))))
    revision = []
    for i in range(2):
        rs = primary["endpoints"]["revision"]["rows"]
        if i >= len(rs):
            break
        r0 = rs[i]
        src = rev_rows.get(r0.get("item_id"))
        revision.append(dict(item_id=r0.get("item_id"), prompt=(src or {}).get("prompt"), versions=(src or {}).get("versions"),
                             conditions=per_condition("revision", i, lambda r: dict(after=[(q["generated"], q["new_exact"], q["old_answer_reappeared"]) for q in r["after_revision_queries"]]))))
    sources = {str(payload): sha(payload), BASE + "/model.safetensors": sha(Path(BASE) / "model.safetensors")}
    sources.update({str(p): sha(p) for p in cells.values()})
    return dict(dataset=dataset, realization=0, order=100, checkpoint=FINAL[dataset], mode=mode, seed=seed, skip=skip,
                stream_positions=[p + 1 for p in positions], stream_length=len(full_order), conditions=list(cells), labels={c: LABEL[c] for c in cells},
                items=rows, locality=locality, near_miss=near, unseen=unseen, revision=revision, sources_sha256=sources)


def render_dataset(d: dict) -> str:
    ds, conds = d["dataset"], d["conditions"]
    which = (f"the first {len(d['items'])} edits" if d.get("mode", "first") == "first" else
             f"{len(d['items'])} edits drawn at random (seed {d['seed']}) from stream positions {d['skip'] + 1}–{d['stream_length']}")
    L = [f"# {ds}: {which} of realization 0, order 100 (checkpoint {d['checkpoint']})", ""]
    if d.get("mode") == "random":
        L.append("Stream positions shown: " + ", ".join(str(p) for p in d["stream_positions"]) + ". Each item's heading gives its position; "
                 "the end-of-stream columns are the same checkpoint as in the first-30 files, so a late item has had fewer later edits "
                 "stored on top of it than an early one.")
        L.append("")
    L.append("Read `Capstan-README.md` first for what each column means. Answers are the exact greedy generations saved in the "
             "cell checkpoints (≤ 32 tokens, stopped at newline/EOS); `⏎` marks a newline, `…` a cut for display. ✓ = scored a "
             "success by the registered alias match (ES / RET-ES / RET-GS), ✗ = not. The **base** rows are the frozen GPT-2's own "
             "answers with no cap (computed on CPU for this document from the sealed Stage-4 base).")
    L.append("")
    # summary counts
    L.append("## Counts over these items")
    L.append("")
    L.append("| condition | immediate ES ✓ | end-of-stream own prompt ✓ | end-of-stream paraphrase ✓ |")
    L.append("|---|---:|---:|---:|")
    for c in conds:
        es = sum(1 for r in d["items"] if (r["conditions"][c]["immediate"] or {}).get("es") == 1.0)
        re_ = sum(1 for r in d["items"] if (r["conditions"][c]["final_prompt"] or {}).get("es") == 1.0)
        gs = sum(1 for r in d["items"] if (r["conditions"][c]["final_paraphrase"] or {}).get("exact"))
        L.append(f"| {d['labels'][c]} | {es}/{len(d['items'])} | {re_}/{len(d['items'])} | {gs}/{len(d['items'])} |")
    L.append("")
    L.append("## The items")
    L.append("")
    for r in d["items"]:
        pos = f" (stream position {r['stream_position']})" if d.get("mode") == "random" else ""
        L.append(f"### {r['index']}. `{r['item_id']}`{pos} — \"{r['prompt']}\"")
        L.append("")
        tt = f" · previously true answer: **{r['target_true']}**" if r.get("target_true") else ""
        L.append(f"- **new target:** {r['target']}{tt}")
        if r["paraphrase"]:
            L.append(f"- **paraphrase:** \"{r['paraphrase']}\"")
        L.append(f"- **base (no cap), prompt:** \"{short(r['base_prompt']['generated'])}\" [{r['base_prompt']['stopped_by']}]"
                 + (f" · **paraphrase:** \"{short(r['base_paraphrase']['generated'])}\"" if r["base_paraphrase"] else ""))
        L.append("")
        L.append("| condition | right after the edit | end of stream, own prompt | end of stream, paraphrase |")
        L.append("|---|---|---|---|")
        for c in conds:
            x = r["conditions"][c]
            im, fp, fq = x["immediate"], x["final_prompt"], x["final_paraphrase"]
            L.append(f"| {d['labels'][c]} | {tick(im and im['es'] == 1.0)} \"{short(im['generated'] if im else None)}\""
                     f"{'' if not im or im['outcome'] == 'accepted' else ' [' + im['outcome'] + ']'} "
                     f"| {tick(fp and fp['es'] == 1.0)} \"{short(fp['generated'] if fp else None)}\" "
                     f"| {tick(fq and fq['exact'])} \"{short(fq['generated'] if fq else None)}\" |")
        L.append("")
    L.append("## Locality prompts (unrelated questions; the cap should leave the base's answer alone)")
    L.append("")
    for e in d["locality"]:
        L.append(f"### `{e['item_id']}` — \"{e['prompt']}\"")
        L.append("")
        L.append("| condition | cap-off (reference) answer | cap answer | preserved |")
        L.append("|---|---|---|---|")
        for c in conds:
            x = e["conditions"].get(c)
            if x:
                L.append(f"| {d['labels'][c]} | \"{short(x['reference'])}\" | \"{short(x['cap'])}\" | {tick(x['preserved'])} |")
        L.append("")
    L.append("## Near-miss cases (an edit, and a neighbouring fact with the same question template that must not change)")
    L.append("")
    for e in d["near_miss"]:
        L.append(f"### `{e['item_id']}` — edit \"{e['edit_prompt']}\" → **{e['edit_answer']}**; neighbour \"{e['neighbour_prompt']}\" (stored answer: {e['neighbour_answer']})")
        L.append("")
        L.append("| condition | edited prompt → cap answer | neighbour → cap-off reference | neighbour → cap answer | neighbour preserved |")
        L.append("|---|---|---|---|---|")
        for c in conds:
            x = e["conditions"].get(c)
            if x:
                L.append(f"| {d['labels'][c]} | {tick(x['edit_exact'])} \"{short(x['edited'])}\" | \"{short(x['neighbour_reference'])}\" | \"{short(x['neighbour_cap'])}\" | {tick(x['preserved'])} |")
        L.append("")
    L.append("## Unseen prompts (facts never stored; the cap should not fire)")
    L.append("")
    for e in d["unseen"]:
        L.append(f"### `{e['item_id']}` — \"{e['prompt']}\" (stored answer in the pool: {e['stored_answer']})")
        L.append("")
        L.append("| condition | cap answer | answer changed vs cap-off |")
        L.append("|---|---|---|")
        for c in conds:
            x = e["conditions"].get(c)
            if x:
                L.append(f"| {d['labels'][c]} | \"{short(x['cap'])}\" | {tick(x['changed'])} |")
        L.append("")
    if d["revision"]:
        L.append("## Revisions (the same fact edited twice; the newer answer must win)")
        L.append("")
        for e in d["revision"]:
            vs = " → ".join(f"v{v['version']}: {v['answer']}" for v in (e["versions"] or []))
            L.append(f"### `{e['item_id']}` — \"{e['prompt']}\" ({vs})")
            L.append("")
            L.append("| condition | answers after the revision (generated, new answer ✓, old answer reappeared) |")
            L.append("|---|---|")
            for c in conds:
                x = e["conditions"].get(c)
                if x:
                    L.append(f"| {d['labels'][c]} | " + "; ".join(f"\"{short(g, 60)}\" {tick(ok)}{' old↩' if old else ''}" for g, ok, old in x["after"]) + " |")
            L.append("")
    return "\n".join(L) + "\n"


README = """# Support information: what the caps actually say — worked examples (Capstan, {date})

This folder shows concrete inputs and outputs behind the headline numbers, so that anyone can see what an "edit", a
"paraphrase", a "locality prompt" or a "near-miss" looks like and what each cap generated. Nothing here is a new
measurement: every answer is the greedy generation saved in the Stage-4 confirmatory cells (realization 0, order 100,
end-of-stream checkpoint {cps}), read from the sealed payloads and checkpoint files whose hashes are in `examples.json`.
The one thing computed for this document is the frozen base's own answer to each shown prompt (CPU, no cap).

## Files

- `examples-zsre.md`, `examples-counterfact.md`, `examples-mquake.md`: {n} edits per dataset (the first {n} in the
  stream order), then five locality prompts, five near-miss cases, three unseen prompts and the revision cases, each with
  every condition that ran at that coordinate.
- `examples.json`: the same content, machine-readable, with source hashes.
- **Second set, without the oldest-memories bias:** `README-random-sample.md` and `examples-<dataset>-random.md`, {n}
  edits per dataset drawn at random (fixed seed) from the rest of the stream, with each item's stream position shown.
- Generator: `pc_cap/aw/support_examples.py` (`--mode first` and `--mode random`).

## How to read an item

Each edit is one fact to teach: a **prompt** (zsRE: a question; CounterFact: a sentence stem about a subject; MQuAKE: a
sentence stem whose answer is a single-hop fact used in multi-hop questions), a **new target** answer, and a held-out
**paraphrase** of the prompt. For CounterFact and MQuAKE the previously true answer is shown too; the edit is
counterfactual by design. The **base** line is what frozen GPT-2 small says with no cap at all: on zsRE questions it
almost always emits a newline at once (an empty answer), on CounterFact stems it continues with fluent but unrelated
prose, on MQuAKE stems it usually gives the old true fact or a guess.

The table under each item has one row per condition and three columns:

1. **right after the edit** — the answer generated immediately after the cap stored this fact (this is what the ES
   score counts; `[code]` marks an acquisition outcome other than `accepted`);
2. **end of stream, own prompt** — the same prompt asked again after all {cps} edits of the stream were stored
   (RET-ES: did the memory survive the later edits?);
3. **end of stream, paraphrase** — the paraphrase asked at the end of the stream (RET-GS: does the cap recognise the
   fact when asked differently?). This is the primary endpoint of the study and where the conditions differ most.

✓ means the registered scorer counted the answer as a success (full-answer alias match after normalisation), ✗ that it
did not. The scorer is strict: a correct answer followed by extra tokens, or a near-synonym not in the alias list, is ✗.

## The conditions

| label | what it is |
|---|---|
| learned reader v5 (primary) | the trained retrieval-and-null network with per-record delta writes; the system the talk is about |
| random-geometry reader + gate | the same gate and delta writes, but the reader's embedding is random (untrained): shows what the geometry alone buys |
| stable v0 cap | the first-month radius-gated cap with its stable write-free keys |
| matched-update adapter | the v0 cap's write rule applied through the v1 interface (a matched-compute comparator) |
| live v0 cap C1 / C2 | the original v0 cap with live keys, routing all three banks (C1) or one chosen bank (C2) |
| continued base (LM / literal) + stable cap | the base further trained on ordinary text (LM) or on the literal edit sentences, then the stable cap on top |

MQuAKE ran only the primary triplet (learned, random, stable v0) at 300 edits.

## Reading the three datasets

- **zsRE.** The base says nothing, so any answer is the cap's. The learned reader answers the paraphrase correctly in
  nearly every case; the random reader gets a third to a half; the v0 caps store the fact (own prompt ✓ right after the
  edit) but mostly cannot find it again from a paraphrase, and their own-prompt retention decays over the stream. Note
  that the {n} items shown are the *first* edits of the stream, i.e. the oldest memories by the end of it, which is
  why the v0 caps' end-of-stream retention here (about 1 in 30) is below their study-wide mean (0.66): their later
  edits overwrite or shadow the earliest ones; the learned reader keeps all of them.
- **CounterFact.** The stems invite free continuation, so the "answers" are short completions. Paraphrases carry a
  distracting prefix sentence; this is where the learned reader's null decision matters and where it still fails on
  roughly a third of items. The v0-family caps never fire on paraphrases here (their calibration matches exact prompts
  only), so their paraphrase column is the base's continuation.
- **MQuAKE.** Single-hop stems; the learned reader retains about 70 % of paraphrases at 300 edits (half of these 30);
  the random reader and stable cap retain none.
- **Unseen prompts.** For facts never stored, a changed answer means the cap fired on some other record (a false
  fire); the random reader does this most often, the v0 caps sometimes (occasionally landing on the right word by
  chance, since answers such as "midfielder" recur in the pool), the learned reader rarely. Whether a record fired is
  not stored in these rows, so only "answer changed" is shown.

## What these examples are not

Thirty hand-readable items per dataset, from one realization and one order; the study's numbers come from 1,000
edits × five orders × three realizations per condition (300 edits on MQuAKE) and are in `pc_cap/docs/R1_stage4_report.md`.
Base answers are shown for context only; they are not an endpoint of the study. Ordinary-text harm (the per-token
loss changes on 245,237 validation positions) is not shown here; see the HT-17 report for that.
"""


README_RANDOM = """# A second set of examples: {n} edits drawn at random from the rest of each stream (Capstan, {date})

The first-30 files (`examples-<dataset>.md`) show the oldest memories of the stream, which biases the end-of-stream
columns against the caps that forget: by checkpoint 1,000 those items have had 970 later edits stored on top of them.
This set removes that bias. For each dataset, {n} stream positions were drawn uniformly at random, without replacement,
from positions {skip}+1 to the end of the stream (1,000 for zsRE and CounterFact, 300 for MQuAKE), with a fixed seed
({seed}) so the draw is reproducible and was made once, before looking at any outcome. Everything else is identical to
the first set: same cells (realization 0, order 100), same checkpoint, same conditions, same scorer, same base-answer
decode. Files: `examples-zsre-random.md`, `examples-counterfact-random.md`, `examples-mquake-random.md`,
`examples-random.json`. Each item's heading gives its stream position, so you can see how many later edits each memory
had to survive.

What the position mix changes (compare each file's counts table with the first-30 file): on zsRE the v0-family caps'
end-of-stream own-prompt retention rises from about 1/30 to 9–13/30 (study-wide mean 0.66 over all 1,000 edits; later
positions have had fewer edits stored on top of them), and their paraphrase retention from 1/30 to 2–4/30; the random
reader's paraphrase retention is 17/30 (first set 11/30; study-wide 0.52); the learned reader keeps all 30 own prompts
and all 30 paraphrases in both sets. On CounterFact the two sets give the same picture (learned 21/30 paraphrases,
random 5/30, v0 family 0/30, own-prompt retention complete for every cap). On MQuAKE the learned reader's paraphrase
retention is 24/30 in this set against 15/30 among the first 30 (study-wide 0.70); the random reader and stable cap
retain none in either. These remain hand-readable samples, not the study's estimates.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--datasets", nargs="+", default=["zsre", "counterfact", "mquake"])
    ap.add_argument("--mode", choices=("first", "random"), default="first")
    ap.add_argument("--seed", type=int, default=20261004)
    ap.add_argument("--skip", type=int, default=30, help="random mode: exclude the first SKIP stream positions")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    answer = base_decoder()
    all_ = {}
    for ds in a.datasets:
        d = build(ds, a.n, answer, mode=a.mode, seed=a.seed, skip=a.skip)
        all_[ds] = d
        suffix = "" if a.mode == "first" else "-random"
        (out / f"examples-{ds}{suffix}.md").write_text(render_dataset(d))
        print(ds, len(d["items"]), "items;", len(d["conditions"]), "conditions")
    import datetime as dt

    if a.mode == "first":
        (out / "examples.json").write_text(json.dumps(all_, ensure_ascii=False, indent=1))
        (out / "Capstan-README.md").write_text(README.format(date=dt.date.today().isoformat(), n=a.n, cps="1,000 (300 for MQuAKE)"))
    else:
        (out / "examples-random.json").write_text(json.dumps(all_, ensure_ascii=False, indent=1))
        (out / "README-random-sample.md").write_text(README_RANDOM.format(date=dt.date.today().isoformat(), n=a.n, seed=a.seed, skip=a.skip))
    print("written to", out)


if __name__ == "__main__":
    main()
