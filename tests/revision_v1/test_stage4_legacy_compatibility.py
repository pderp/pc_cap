"""Explicitly missing legacy result paths retain the complete expected axes."""

import pccap.revision_v1.analysis_stage4 as module


def test_missing_result_paths_normalized_without_pruning_axes(monkeypatch):
    observed = []

    def fake_analyze(inv, **kwargs):
        observed.append(inv)
        assert inv["axes"]["conditions"] == ["v2", "v3"]
        assert inv["cells"] == [{"condition": "v3", "stream_dir": "declared/path"}]
        return {"status": "fixture"}

    monkeypatch.setattr(module, "analyze", fake_analyze)
    inv = {
        "scope": "development",
        "axes": {"conditions": ["v2", "v3"]},
        "cells": [
            {"condition": "v2", "stream_dir": None},
            {"condition": "v3", "stream_dir": "declared/path"},
        ],
    }
    result = module.development_dry_run(inv)
    assert len(inv["cells"]) == 2
    assert result["registered_inventory"]["registered_cells"] == 360
    assert len(observed) == 1
