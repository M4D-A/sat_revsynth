import pytest
from random import randint, sample
from copy import copy
from .circuit import Circuit, Gate, TruthTable


max_bits_num = 4
epochs = 2**8
bits_num_randomizer = list(randint(3, max_bits_num) for _ in range(epochs))


@pytest.fixture
def x_params(bits_num):
    target = randint(0, bits_num - 1)
    return target


@pytest.fixture
def cx_params(bits_num):
    control, target = sample(range(0, bits_num - 1), 2)
    return control, target


@pytest.fixture
def mcx_params(bits_num):
    special_ids_num = randint(2, bits_num - 1)
    target, *controls = sample(range(0, bits_num - 1), special_ids_num)
    return controls, target


@pytest.fixture
def random_circuit(bits_num):
    gates_num = randint(2, 32)
    circ = Circuit(bits_num)
    for _ in range(gates_num):
        controls_num = randint(0, bits_num - 2)
        ids = sample(range(0, bits_num - 1), controls_num + 1)
        target = ids[0]
        controls = [] if len(ids) == 1 else ids[1:]
        circ.append(Gate((list(controls), target)))
    return circ


@pytest.fixture
def empty_circuit(bits_num):
    circ = Circuit(bits_num)
    return circ


@pytest.fixture
def identity_tt(bits_num):
    return TruthTable(bits_num)
#
#
# @pytest.fixture
# def random_gate_list(bits_num):
#     gates: list[Gate] = []
#     gates_num = randint(2, 32)
#     for _ in range(gates_num):
#         controls_num = randint(0, bits_num - 2)
#         ids = sample(range(0, bits_num - 1), controls_num + 1)
#         target = ids[0]
#         controls = [] if len(ids) == 1 else ids[1:]
#         gates.append(Gate((list(controls), target)))
#     return gates


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_x(x_params, random_circuit):
    size = len(random_circuit)
    target = x_params
    circ = copy(random_circuit)
    circ.x(target)
    assert len(circ) == size + 1
    assert circ.gates()[-1] == ([], target)
    for ref_row, row in zip(random_circuit.tt().bits(), circ.tt().bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_cx(cx_params, random_circuit):
    size = len(random_circuit)
    control, target = cx_params
    circ = copy(random_circuit)
    circ.cx(control, target)
    assert len(circ) == size + 1
    assert circ.gates()[-1] == ([control], target)
    for ref_row, row in zip(random_circuit.tt().bits(), circ.tt().bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and row[control] == 1:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_mcx(mcx_params, random_circuit):
    size = len(random_circuit)
    controls, target = mcx_params
    circ = copy(random_circuit)
    circ.mcx(controls, target)
    assert len(circ) == size + 1
    assert circ.gates()[-1] == (sorted(controls), target)
    for ref_row, row in zip(random_circuit.tt().bits(), circ.tt().bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and all(row[c] for c in controls):
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_x_involutivity(x_params, empty_circuit, identity_tt):
    target = x_params
    empty_circuit.x(target)
    empty_circuit.x(target)
    assert len(empty_circuit) == 2
    assert all(gate == ([], target) for gate in empty_circuit.gates())
    assert empty_circuit.tt() == identity_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_cx_involutivity(cx_params, empty_circuit, identity_tt):
    control, target = cx_params
    empty_circuit.cx(control, target)
    empty_circuit.cx(control, target)
    assert len(empty_circuit) == 2
    assert all(gate == ([control], target) for gate in empty_circuit.gates())
    assert empty_circuit.tt() == identity_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_mcx_involutivity(mcx_params, empty_circuit, identity_tt):
    controls, target = mcx_params
    empty_circuit.mcx(controls, target)
    empty_circuit.mcx(controls, target)
    assert len(empty_circuit) == 2
    assert all(gate == (sorted(controls), target) for gate in empty_circuit.gates())
    assert empty_circuit.tt() == identity_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_inplace(empty_circuit, identity_tt):
    circ_a = copy(empty_circuit)
    target = 0
    circ_b = circ_a.x(target, inplace=False)

    assert circ_a == empty_circuit
    assert circ_a.tt() == identity_tt

    assert circ_b != empty_circuit
    assert circ_b == empty_circuit.x(target, inplace=False)
    assert circ_b.tt() == identity_tt.x(target, inplace=False)

    circ_a.x(target, inplace=True)
    assert circ_a != empty_circuit
    assert circ_b != empty_circuit
    assert circ_b == circ_a

    circ_a.pop()
    circ_b.pop()
    assert circ_a == empty_circuit
    assert circ_b == empty_circuit
    assert circ_b == circ_a


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_reverse(random_circuit, identity_tt):
    reversed_circuit = random_circuit.reverse(inplace=False)
    assert (random_circuit + reversed_circuit).tt() == identity_tt
    assert (reversed_circuit + random_circuit).tt() == identity_tt
    assert len(random_circuit + reversed_circuit) == 2 * len(random_circuit)
    assert len(reversed_circuit + random_circuit) == 2 * len(random_circuit)


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_rotate(random_circuit):
    size = len(random_circuit)
    shift = randint(-3*size, 3*size)
    rotated_circuit = random_circuit.rotate(shift, inplace=False)
    assert len(random_circuit) == len(rotated_circuit)
    for i, shifted_gate in enumerate(rotated_circuit.gates()):
        gate = random_circuit.gates()[(i+shift) % size]
        assert shifted_gate == gate
    re_rotated_circuit = rotated_circuit.rotate(-shift, inplace=False)
    assert re_rotated_circuit == random_circuit
