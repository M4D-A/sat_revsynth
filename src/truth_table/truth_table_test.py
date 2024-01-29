import pytest
from random import randint, sample
from .truth_table import TruthTable

from copy import deepcopy


max_tt_size = 8
epochs = 128
size_randomizer = list(randint(3, max_tt_size) for _ in range(epochs))


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_x(tt_size):
    ref_tt = TruthTable(tt_size).shuffle()
    tt = deepcopy(ref_tt)
    target = randint(0, tt.bits_num() - 1)
    tt.x(target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_cx(tt_size):
    ref_tt = TruthTable(tt_size).shuffle()
    tt = deepcopy(ref_tt)
    control, target = sample(range(0, tt.bits_num() - 1), 2)
    tt.cx(control, target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and row[control] == 1:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_mcx(tt_size):
    ref_tt = TruthTable(tt_size).shuffle()
    tt = deepcopy(ref_tt)
    special_ids_num = randint(2, tt.bits_num() - 1)
    target, *controls = sample(range(0, tt.bits_num() - 1), special_ids_num)
    tt.mcx(controls, target)
    for ref_row, row in zip(ref_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and all(row[c] for c in controls):
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_x_involutivity(tt_size):
    ref_tt = TruthTable(tt_size).shuffle()
    tt = deepcopy(ref_tt)
    target = randint(0, tt.bits_num() - 1)
    tt.x(target)
    tt.x(target)
    assert tt == ref_tt


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_cx_involutivity(tt_size):
    ref_tt = TruthTable(tt_size).shuffle()
    tt = deepcopy(ref_tt)
    control, target = sample(range(0, tt.bits_num() - 1), 2)
    tt.cx(control, target)
    tt.cx(control, target)
    assert tt == ref_tt


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_mcx_involutivity(tt_size):
    ref_tt = TruthTable(tt_size).shuffle()
    tt = deepcopy(ref_tt)
    special_ids_num = randint(2, tt.bits_num() - 1)
    target, *controls = sample(range(0, tt.bits_num() - 1), special_ids_num)
    tt.mcx(controls, target)
    tt.mcx(controls, target)
    assert tt == ref_tt
