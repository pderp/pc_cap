"""Reduced execution never contracts the multiplicity family or fabricates1000."""

import copy

import pytest
from scripts.r1_49g_inference import primary_contrasts, validate_family
from scripts.r1_49g_secondary import cell_benchmarks
from scripts.r1_d9_layouts import digest, production

from tests.revision_v1.test_r1_49g_analysis import synthetic_matrix


def reduced():
    m, loaded = synthetic_matrix()
    m.update(
        name="run_matrix_v5_2_option_D",
        option="D",
        dataset_layouts=production("D"),
        layout_sha256=digest(production("D")),
    )
    m["axes"].pop("realizations")
    m["axes"]["realizations_by_dataset"] = {d: [0, 1, 2] for d in production("D")}
    for c in m["cells"]:
        if c["dataset"] == "mquake":
            c["checkpoints"] = [100, 300]
            c["population"] = copy.deepcopy(c["population"])
            c["population"]["item_ids"] = c["population"]["item_ids"][:300]
            c["population"]["paraphrase_counts"] = c["population"]["paraphrase_counts"][:300]
    return m, loaded


def test_two_datasets_identical_and_seven_mquake_claims_unavailable_even_if_spoofed():
    original, loaded = synthetic_matrix()
    baseline = primary_contrasts(original, loaded)
    m, _ = reduced()
    results = primary_contrasts(m, loaded)
    assert results[:14] == baseline[:14]
    assert len(results) == 21 and sum(r["interval_count"] for r in results) == 63
    assert all(r["classification"] == "unavailable" for r in results[14:])
    assert all(r["metrics"]["RET-GS"]["adjusted_interval"] is None for r in results[14:])
    m["cells"][-1]["checkpoints"] = [100, 300, 1000]
    with pytest.raises(ValueError, match="cadence"):
        validate_family(m)


def test_actual300_is_descriptive_and_requires_occupancy_not_attempts():
    m, loaded = reduced()
    c = next(c for c in m["cells"] if c["dataset"] == "mquake")
    expected = c["population"]["endpoints"]["unseen"]

    def report(n):
        return dict(
            observation=dict(active_records_status="ok", active_records=n),
            unseen={
                "rows": [
                    dict(item_id=i, status="ok", firing_status="ok", false_fire=False)
                    for i in expected
                ]
            },
        )

    result = cell_benchmarks(c, {}, {100: report(100), 300: report(300)})
    assert result["actual_occupancy_descriptive"]["value"] == 0
    assert result["actual_occupancy_descriptive"]["passes"] is None
    assert result["benchmarks"]["unseen_1000"]["status"] == "unavailable"
    result = cell_benchmarks(c, {}, {300: report(299)})
    assert result["actual_occupancy_descriptive"]["value"] is None
