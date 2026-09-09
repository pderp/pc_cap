"""CAP-03 / PC-6: byte ceiling, nominal capacities, wide keys, equal ceilings across arms."""

import pytest

from pccap.cap import memory


def test_b_cap_reference_value():
    assert memory.b_cap(768) == 38_535_168


@pytest.mark.parametrize("arm", ["C0", "C1", "C2", "CR", "CO"])
def test_sum_of_bank_ceilings_equals_b_cap(arm):
    c = memory.bank_ceilings(arm, 768)
    assert sum(c.values()) == memory.b_cap(768)
    if arm == "C0":
        assert list(c) == [3]
    else:
        assert c[1] == c[2] == 12_845_056 and c[3] == 12_845_056


def test_nominal_capacities_zero_overhead():
    d = 768
    assert memory.capacity(memory.b_cap(d), d, d) == 6144
    assert memory.capacity(memory.bank_ceilings("C1", d)[1], d, d) == 2048
    assert memory.capacity(memory.bank_ceilings("C1", d)[1], 2 * d, d) == 1374


def test_overhead_reduces_capacity_and_is_reported():
    d = 768
    B = memory.bank_ceilings("C1", d)[1]
    nominal = memory.capacity(B, d, d)
    with_overhead = memory.capacity(B, d, d, fixed_overhead=10_000)
    assert with_overhead <= nominal and with_overhead == 2046
    lay = memory.BankLayout.plan(1, B, d, d, fixed_overhead=10_000)
    assert lay.capacity == 2046 and lay.allocated_bytes() <= B
    with pytest.raises(ValueError):
        memory.capacity(B, d, d, fixed_overhead=-1)


def test_wide_keys_reduce_capacity():
    d = 768
    B = memory.bank_ceilings("C2", d)[2]
    assert memory.capacity(B, 2 * d, d) < memory.capacity(B, d, d)


def test_unknown_arm():
    with pytest.raises(ValueError):
        memory.bank_ceilings("B1", 768)
