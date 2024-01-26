import pytest
from random import randint, sample
from .truth_table import TruthTable


max_tt_size = 8
epochs = 16
size_randomizer = (randint(1, max_tt_size) for _ in range(epochs))


@pytest.mark.parametrize("tt_size", list(size_randomizer))
def test_not_involutivity(tt_size):
    ref_tt = TruthTable(tt_size)
    tt = TruthTable(tt_size)
    target = randint(0, tt.bits_num() - 1)
    tt.nott(target)
    tt.nott(target)
    assert tt == ref_tt
