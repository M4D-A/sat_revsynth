import pytest
from random import randint, sample
from .truth_table import TruthTable


max_tt_size = 8
epochs = 128
size_randomizer = list(randint(3, max_tt_size) for _ in range(epochs))


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_not_involutivity(tt_size):
    ref_tt = TruthTable(tt_size)
    tt = TruthTable(tt_size)
    target = randint(0, tt.bits_num() - 1)
    tt.nott(target)
    tt.nott(target)
    assert tt == ref_tt


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_cnot_involutivity(tt_size):
    ref_tt = TruthTable(tt_size)
    tt = TruthTable(tt_size)
    control, target = sample(range(0, tt.bits_num() - 1), 2)
    tt.cnot(control, target)
    tt.cnot(control, target)
    assert tt == ref_tt


@pytest.mark.parametrize("tt_size", size_randomizer)
def test_mcnot_involutivity(tt_size):
    ref_tt = TruthTable(tt_size)
    tt = TruthTable(tt_size)
    special_ids_num = randint(3, tt.bits_num())
    target, *controls = sample(range(0, tt.bits_num() - 1), special_ids_num)
    tt.mcnot(controls, target)
    tt.mcnot(controls, target)
    assert tt == ref_tt
