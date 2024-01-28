import pytest
from random import randint
from .circuit import Circuit
from copy import deepcopy


max_tt_size = 8
epochs = 128
size_randomizer = list(randint(3, max_tt_size) for _ in range(epochs))


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_not(circ_size):
    ref_circ = Circuit(circ_size)
    circ = deepcopy(ref_circ)
    target = randint(0, circ.width() - 1)
    circ.x(target)
    for ref_row, row in zip(ref_circ.tt().bits(), circ.tt().bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target:
                assert ref_b != b
            else:
                assert ref_b == b
