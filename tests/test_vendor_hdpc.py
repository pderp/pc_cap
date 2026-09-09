"""ENV-04: the sibling reference is pinned, readable, and never imported."""

import subprocess
import sys

import pytest

from pccap import vendor_hdpc


def test_pinned_commit_recorded():
    info = vendor_hdpc.inspect()
    assert info["commit"] == vendor_hdpc.PINNED_COMMIT
    assert info["licence"] == "unknown"
    assert "torch" in info["pins"]


@pytest.mark.parametrize("name", ["wrap", "energy", "relax", "checkpoint", "train_distill"])
def test_reference_files_exist(name):
    assert vendor_hdpc.reference(name).exists()


def test_unknown_reference_is_structured():
    with pytest.raises(vendor_hdpc.SiblingUnavailable) as e:
        vendor_hdpc.reference("nope")
    assert e.value.payload["status"] == "unavailable"


def test_hdpc_never_imported_by_pccap():
    """Importing every pccap module must not import hdpc or torch (DEC-001/DEC-003)."""
    code = (
        "import pkgutil, importlib, sys, pccap\n"
        "for m in pkgutil.walk_packages(pccap.__path__, 'pccap.'):\n"
        "    importlib.import_module(m.name)\n"
        "bad = [m for m in sys.modules if m == 'hdpc' or m.startswith('hdpc.') or m == 'torch']\n"
        "print(bad)\n"
    )
    out = subprocess.check_output([sys.executable, "-c", code], text=True)
    assert out.strip() == "[]", out
