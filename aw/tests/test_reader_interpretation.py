"""Reporting must preserve seed reversals, endpoint differences and partial pairs."""

from aw.reader_interpretation import narrative


def cell(rule, seed, dataset, retention, fired, own=1):
    return dict(
        rule=rule,
        seed=seed,
        dataset=dataset,
        status="complete",
        metrics={"RET-GS": {"value": retention}, "RET-ES": {"value": own}},
        gate={"selected": fired, "logical_positions": 245237},
        harm={"capoff": {"mean_delta_nll": fired / 245237, "es99_positive": fired / 2452.37}},
    )


def test_two_seed_reversal_and_unequal_own_prompt_retention():
    cells = [
        cell(rule, seed, "zsre", 0.99 if rule == "bp" else 0.97, 13 if rule == "bp" else 6)
        for rule in ("bp", "epc")
        for seed in (0, 1)
    ]
    cells += [
        cell("bp", 0, "counterfact", 0.81, 256),
        cell("epc", 0, "counterfact", 0.5683333333, 185),
        cell("bp", 1, "counterfact", 0.8, 660, 0.99),
        cell("epc", 1, "counterfact", 0.7783333333, 720),
    ]
    text = narrative({"cells": cells})
    assert "0, 1 (2/3 planned)" in text
    assert "2.00 to 24.17 percentage points" in text
    assert "direction reverses across seeds" in text
    assert "counterfact | 1 | 0.99 | 1 |" in text
    assert "comparison remains partial" in text


def test_one_dataset_does_not_complete_another_seed():
    cells = [cell(rule, 0, ds, 0.9, 1) for rule in ("bp", "epc") for ds in ("zsre", "counterfact")]
    cells += [cell(rule, 1, "zsre", 0.9, 1) for rule in ("bp", "epc")]
    text = narrative({"cells": cells})
    assert "seeds: 0 (1/3 planned)" in text
    assert "lower in every" not in text
    assert "direction reverses" not in text


def test_complete_three_seed_reading_preserves_dataset_specific_reversal():
    cells = []
    for seed in range(3):
        for ds in ('zsre', 'counterfact'):
            cells.append(cell('bp', seed, ds, .8, 10))
            cells.append(cell('epc', seed, ds, .81 if ds == 'zsre' and seed == 2 else .7,
                              5 if seed == 0 else 20))
    text = narrative({'cells': cells})
    assert '0, 1, 2 (3/3 planned)' in text
    assert 'On zsre, ePC paraphrase retention is lower in 2/3' in text
    assert 'On counterfact, ePC paraphrase retention is lower in 3/3' in text
    assert 'lower in every fully paired row' not in text
    assert 'comparison remains partial' not in text
    assert 'mean_delta_nll, ePC−BP by seed (0, 1, 2)' in text
