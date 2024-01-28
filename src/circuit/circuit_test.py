import pytest
from random import randint, sample
from .circuit import Circuit
from copy import deepcopy


max_tt_size = 8
epochs = 128
size_randomizer = list(randint(3, max_tt_size) for _ in range(epochs))


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_x(circ_size):
    ref_circ = Circuit(circ_size)
    circ = deepcopy(ref_circ)
    target = randint(0, circ.width() - 1)
    circ.x(target)
    assert len(circ) == 1
    assert circ.gates()[0] == ([], target)
    for ref_row, row in zip(ref_circ.tt().bits(), circ.tt().bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_cx(circ_size):
    ref_circ = Circuit(circ_size)
    circ = deepcopy(ref_circ)
    control, target = sample(range(0, circ_size - 1), 2)
    circ.cx(control, target)
    assert len(circ) == 1
    assert circ.gates()[0] == ([control], target)
    for ref_row, row in zip(ref_circ.tt().bits(), circ.tt().bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and row[control] == 1:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_mcx(circ_size):
    ref_circ = Circuit(circ_size)
    circ = deepcopy(ref_circ)
    special_ids_num = randint(2, circ_size - 1)
    target, *controls = sample(range(0, circ_size - 1), special_ids_num)
    circ.mcx(controls, target)
    assert len(circ) == 1
    assert circ.gates()[0] == (sorted(controls), target)
    for ref_row, row in zip(ref_circ.tt().bits(), circ.tt().bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and all(row[c] for c in controls):
                assert ref_b != b
            else:
                assert ref_b == b
