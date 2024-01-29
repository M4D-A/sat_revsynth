import pytest
from random import randint, sample
from .truth_table import TruthTable
from copy import copy

max_tt_size = 8
epochs = 2**8
size_randomizer = list(randint(3, max_tt_size) for _ in range(epochs))


def x_params(bits_num):
    target = randint(0, bits_num - 1)
    return target


def cx_params(bits_num):
    control, target = sample(range(0, bits_num - 1), 2)
    return control, target


def mcx_params(bits_num):
    special_ids_num = randint(2, bits_num - 1)
    target, *controls = sample(range(0, bits_num - 1), special_ids_num)
    return controls, target


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_x(tt_size):
    ref_tt = TruthTable(tt_size).shuffle(inplace=False)
    tt = copy(ref_tt)

    target = x_params(tt_size)
    tt.x(target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_cx(tt_size):
    ref_tt = TruthTable(tt_size).shuffle(inplace=False)
    tt = copy(ref_tt)
    control, target = cx_params(tt_size)
    tt.cx(control, target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and row[control] == 1:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_mcx(tt_size):
    ref_tt = TruthTable(tt_size).shuffle(inplace=False)
    tt = copy(ref_tt)
    controls, target = mcx_params(tt_size)
    tt.mcx(controls, target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and all(row[c] for c in controls):
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_x_involutivity(tt_size):
    ref_tt = TruthTable(tt_size).shuffle(inplace=False)
    tt = copy(ref_tt)
    target = x_params(tt_size)
    tt.x(target)
    tt.x(target)
    assert tt == ref_tt


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_cx_involutivity(tt_size):
    ref_tt = TruthTable(tt_size).shuffle(inplace=False)
    tt = copy(ref_tt)
    control, target = cx_params(tt_size)
    tt.cx(control, target)
    tt.cx(control, target)
    assert tt == ref_tt


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_mcx_involutivity(tt_size):
    ref_tt = TruthTable(tt_size).shuffle(inplace=False)
    tt = copy(ref_tt)
    controls, target = mcx_params(tt_size)
    tt.mcx(controls, target)
    tt.mcx(controls, target)
    assert tt == ref_tt


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_inplace(tt_size):
    tt_a = TruthTable(tt_size)
    target = x_params(tt_size)

    tt_b = tt_a.x(target, inplace=False)
    assert tt_a == TruthTable(tt_size)
    assert tt_b != TruthTable(tt_size)

    tt_a.x(target, inplace=True)
    assert tt_a != TruthTable(tt_size)
    assert tt_b != TruthTable(tt_size)
    assert tt_b == tt_a
