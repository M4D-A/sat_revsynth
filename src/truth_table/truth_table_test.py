import pytest
from random import randint
from copy import copy
from .truth_table import TruthTable
from ..utils.params import x_params, cx_params, mcx_params


max_bits_size = 8
epochs = 2**8
bits_num_randomizer = list(randint(3, max_bits_size) for _ in range(epochs))


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_x(bits_num):
    ref_tt = TruthTable(bits_num).shuffle()
    tt = copy(ref_tt)

    target = x_params(bits_num)
    tt.x(target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_cx(bits_num):
    ref_tt = TruthTable(bits_num).shuffle()
    tt = copy(ref_tt)
    control, target = cx_params(bits_num)
    tt.cx(control, target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and row[control] == 1:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_mcx(bits_num):
    ref_tt = TruthTable(bits_num).shuffle()
    tt = copy(ref_tt)
    controls, target = mcx_params(bits_num)
    tt.mcx(controls, target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and all(row[c] for c in controls):
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_x_involutivity(bits_num):
    ref_tt = TruthTable(bits_num).shuffle()
    tt = copy(ref_tt)
    target = x_params(bits_num)
    tt.x(target)
    tt.x(target)
    assert tt == ref_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_cx_involutivity(bits_num):
    ref_tt = TruthTable(bits_num).shuffle()
    tt = copy(ref_tt)
    control, target = cx_params(bits_num)
    tt.cx(control, target)
    tt.cx(control, target)
    assert tt == ref_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_mcx_involutivity(bits_num):
    ref_tt = TruthTable(bits_num).shuffle()
    tt = copy(ref_tt)
    controls, target = mcx_params(bits_num)
    tt.mcx(controls, target)
    tt.mcx(controls, target)
    assert tt == ref_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_inplace(bits_num):
    tt_a = TruthTable(bits_num)
    target = x_params(bits_num)

    tt_b = tt_a.x(target, inplace=False)
    assert tt_a == TruthTable(bits_num)
    assert tt_b != TruthTable(bits_num)

    tt_a.x(target, inplace=True)
    assert tt_a != TruthTable(bits_num)
    assert tt_b != TruthTable(bits_num)
    assert tt_b == tt_a

    tt_a.x(target)
    tt_b.x(target)
    assert tt_a == TruthTable(bits_num)
    assert tt_b == TruthTable(bits_num)
    assert tt_b == tt_a
