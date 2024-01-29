import pytest
from random import randint, sample
from copy import copy
from .circuit import Circuit, Gate, TruthTable
from ..utils.params import x_params, cx_params, mcx_params


max_bits_num = 4
epochs = 2**8
size_randomizer = list(randint(3, max_bits_num) for _ in range(epochs))


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_x(circ_size):
    ref_circ = Circuit(circ_size)
    ref_circ._tt.shuffle()
    circ = copy(ref_circ)
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
    ref_circ._tt.shuffle()
    circ = copy(ref_circ)
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
    ref_circ._tt.shuffle()
    circ = copy(ref_circ)
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


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_x_involutivity(circ_size):
    circ = Circuit(circ_size)
    target = randint(0, circ_size - 1)
    circ.x(target)
    circ.x(target)
    assert len(circ) == 2
    assert all(gate == ([], target) for gate in circ.gates())
    assert circ.tt() == TruthTable(circ_size)


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_cx_involutivity(circ_size):
    circ = Circuit(circ_size)
    control, target = sample(range(0, circ_size - 1), 2)
    circ.cx(control, target)
    circ.cx(control, target)
    assert len(circ) == 2
    assert all(gate == ([control], target) for gate in circ.gates())
    assert circ.tt() == TruthTable(circ_size)


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_mcx_involutivity(circ_size):
    circ = Circuit(circ_size)
    special_ids_num = randint(2, circ_size - 1)
    target, *controls = sample(range(0, circ_size - 1), special_ids_num)
    circ.mcx(controls, target)
    circ.mcx(controls, target)
    assert len(circ) == 2
    assert all(gate == (sorted(controls), target) for gate in circ.gates())
    assert circ.tt() == TruthTable(circ_size)


@pytest.mark.parametrize("circ_size", size_randomizer)
def test_complex_involution(circ_size):
    gates: list[Gate] = []
    gates_num = randint(2, 32)
    for _ in range(gates_num):
        controls_num = randint(0, circ_size - 2)
        ids = sample(range(0, circ_size - 1), controls_num + 1)
        target = ids[0]
        controls = [] if len(ids) == 1 else ids[1:]
        gates.append(Gate((list(controls), target)))

    circ = Circuit(circ_size)
    for gate in gates:
        circ.append(gate)
    for gate in reversed(gates):
        circ.append(gate)

    for i, g in enumerate(circ.gates()):
        if i < gates_num:
            controls, target = gates[i]
        else:
            controls, target = gates[len(circ) - i - 1]
        assert g == (sorted(controls), target)

    assert len(circ) == 2 * gates_num
    assert circ.tt() == TruthTable(circ_size)


@pytest.mark.parametrize("circ_size", [3])
def test_inplace(circ_size):
    circ_a = Circuit(circ_size)
    target = 0
    circ_b = circ_a.x(target, inplace=False)

    assert circ_a == Circuit(circ_size)
    assert circ_a.tt() == TruthTable(circ_size)

    assert circ_b != Circuit(circ_size)
    assert circ_b == Circuit(circ_size).x(target)
    assert circ_b.tt() == TruthTable(circ_size).x(target)

    circ_a.x(target, inplace=True)
    assert circ_a != Circuit(circ_size)
    assert circ_b != Circuit(circ_size)
    assert circ_b == circ_a

    circ_a.pop()
    circ_b.pop()
    assert circ_a == Circuit(circ_size)
    assert circ_b == Circuit(circ_size)
    assert circ_b == circ_a