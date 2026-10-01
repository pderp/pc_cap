"""Option R: synthetic session costs and paired subject-realization sensitivities."""

import copy
import json

import pytest

from aw import r_report as r


def fixture():
    cells = []
    for ds in r.rr.DATASETS:
        for realization in range(4):
            for order in range(100, 105):
                for condition in r.CONDITIONS[:2]:
                    value = 0.2 + (0.1 * realization if condition == "R1_learned_ff" else 0)
                    cells.append(
                        dict(
                            cell=dict(
                                dataset=ds,
                                realization=realization,
                                order=order,
                                condition=condition,
                            ),
                            artifact_complete=True,
                            endpoint_complete=True,
                            checkpoints={
                                str(n): dict(
                                    population_identity=f"{ds}-{realization}-{order}",
                                    primary={
                                        k: dict(value=value, status="complete") for k in r.PRIMARY
                                    },
                                )
                                for n in (100, 300, 1000)
                            },
                        )
                    )
    return cells


def test_four_subject_means_t3_not_twenty_orders():
    result = r.sensitivity(fixture())[0]
    assert result["estimate"] == pytest.approx(0.15)
    # SD(.0,.1,.2,.3)/sqrt(4); five orders must not shrink this SE.
    half = r.T3_975 * (0.05 / 3) ** 0.5 / 2
    assert result["interval"] == pytest.approx([0.15 - half, 0.15 + half])
    assert result["df"] == 3


def test_missing_one_order_withholds_t3_and_duplicate_is_error():
    cells = fixture()
    cells.pop()
    result = next(x for x in r.sensitivity(cells) if x["dataset"] == "counterfact")
    assert result["estimate"] is None and result["interval"] is None
    assert result["realizations"][3]["paired_orders"] == 4
    assert result["realizations"][3]["mean"] is None
    with pytest.raises(ValueError, match="duplicate"):
        r.sensitivity(cells + [copy.deepcopy(cells[0])])


def test_incomplete_final_and_population_mismatch_excluded():
    cells = fixture()
    cells[0]["artifact_complete"] = False
    assert r.sensitivity(cells)[0]["interval"] is None
    cells[0]["artifact_complete"] = True
    cells[0]["checkpoints"]["100"]["population_identity"] = "wrong"
    with pytest.raises(ValueError, match="population differs"):
        r.sensitivity(cells)


def test_session_resumes_count_once_no_idle_gap_or_child_cost(tmp_path):
    binding = dict(path="matrix", sha256="hash")
    for folder, seconds in [
        (tmp_path, 10),
        (tmp_path / "resumes/second", 7),
        (tmp_path / "resumes/open", None),
    ]:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "session-start.json").write_text(json.dumps(dict(matrix=binding)))
        if seconds is not None:
            (folder / "session-finish.json").write_text(
                json.dumps(dict(elapsed_wall_seconds=seconds, process_seconds=99))
            )
    rows = r.segments(tmp_path, {}, binding)
    assert sum(x["elapsed_wall_seconds"] or 0 for x in rows) == 17
    assert sum(x["status"] == "open" for x in rows) == 1
    with pytest.raises(ValueError, match="matrix identity"):
        r.segments(tmp_path, {}, dict(path="wrong", sha256="hash"))
