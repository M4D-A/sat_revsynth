import pytest
from random import randint, sample, shuffle
from copy import copy
from circuit.circuit import Circuit, Gate, TruthTable


max_bits_num = 5
max_gates_num = 6
epochs = 2**6
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
    gates_num = randint(2, max_gates_num)
    circ = Circuit(bits_num)
    for _ in range(gates_num):
        controls_num = randint(0, bits_num - 2)
        ids = sample(range(0, bits_num), controls_num + 1)
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


@pytest.fixture
def random_permutations(bits_num):
    permutation = list(range(bits_num))
    shuffle(permutation)
    inv_permutation = [0] * bits_num
    for i, v in enumerate(permutation):
        inv_permutation[v] = i
    return (permutation, inv_permutation)


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
    reversed_circuit = random_circuit.reverse()
    assert (random_circuit + reversed_circuit).tt() == identity_tt
    assert (reversed_circuit + random_circuit).tt() == identity_tt
    assert len(random_circuit + reversed_circuit) == 2 * len(random_circuit)
    assert len(reversed_circuit + random_circuit) == 2 * len(random_circuit)


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_rotate(random_circuit):
    size = len(random_circuit)
    shift = randint(-3*size, 3*size)
    rotated_circuit = random_circuit.rotate(shift)
    assert len(random_circuit) == len(rotated_circuit)
    for i, shifted_gate in enumerate(rotated_circuit.gates()):
        gate = random_circuit.gates()[(i+shift) % size]
        assert shifted_gate == gate
    re_rotated_circuit = rotated_circuit.rotate(-shift)
    assert re_rotated_circuit == random_circuit


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_permute(random_circuit, random_permutations):
    permutation, inv_permutation = random_permutations
    permuted_circuit = random_circuit.permute(permutation)
    assert permuted_circuit.tt() == random_circuit.tt().permute(
        permutation, permute_input=True)
    re_permuted_circuit = permuted_circuit.permute(inv_permutation)
    assert re_permuted_circuit == random_circuit

    recreated_circuit = Circuit(random_circuit.width())
    for _, gate in enumerate(permuted_circuit.gates()):
        recreated_circuit.append(gate, inplace=True)
    assert permuted_circuit == recreated_circuit


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_swap(random_circuit):
    swap_id = randint(0, len(random_circuit) - 1)
    swapped = random_circuit.swap(swap_id)
    assert len(swapped) == len(random_circuit)
    assert swapped[swap_id] == random_circuit[(swap_id + 1) % len(swapped)]
    assert random_circuit[swap_id] == swapped[(swap_id + 1) % len(swapped)]
    for i, (gate_a, gate_b) in enumerate(zip(swapped, random_circuit)):
        if i not in [swap_id, (swap_id + 1) % len(swapped)]:
            assert gate_a == gate_b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_permutations(bits_num):
    circuit = Circuit(bits_num).cx(0, 1)
    permutations = circuit.permutations()
    assert len(permutations) == bits_num * (bits_num-1)

    circuit = Circuit(bits_num).x(0)
    permutations = circuit.permutations()
    assert len(permutations) == bits_num

    circuit = Circuit(bits_num).mcx([0, 1], 2)
    permutations = circuit.permutations()
    assert len(permutations) == bits_num * (bits_num - 1) * (bits_num - 2) / 2

    circuit = Circuit(bits_num).cx(0, 1).x(1)
    permutations = circuit.permutations()
    assert len(permutations) == bits_num * (bits_num-1)

    circuit = Circuit(bits_num).x(0).x(1)
    permutations = circuit.permutations()
    assert len(permutations) == bits_num * (bits_num-1)

    circuit = Circuit(bits_num).mcx([0, 1], 2).mcx([0, 2], 1)
    permutations = circuit.permutations()
    assert len(permutations) == bits_num * (bits_num - 1) * (bits_num - 2)


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_rotations(random_circuit):
    rotations = random_circuit.rotations()
    assert len(rotations) <= len(random_circuit)


def test_unroll():
    circuit = Circuit(2)
    circuit.x(0).x(1)
    swap_space = circuit.unroll()
    assert len(swap_space) == 2
    assert circuit in swap_space
    assert Circuit(2).x(1).x(0) in swap_space

    circuit = Circuit(2)
    circuit.x(0).cx(0, 1)
    swap_space = circuit.unroll()
    assert len(swap_space) == 4
    assert circuit in swap_space
    assert Circuit(2).x(1).cx(1, 0)
    assert Circuit(2).cx(0, 1).x(0) in swap_space
    assert Circuit(2).cx(1, 0).x(1) in swap_space

    circuit = Circuit(3)
    circuit.x(0).mcx([1, 2], 0).x(0)
    swap_space = circuit.unroll()
    assert len(swap_space) == 9
    assert circuit in swap_space
    circuit.mcx([1, 2], 0).x(0).x(0)
    circuit.x(1).mcx([2, 0], 1).x(1)
    circuit.x(2).x(2).mcx([1, 0], 2)

    circuit = Circuit(3)
    circuit.x(1).mcx([1, 2], 0).x(2)
    swap_space = circuit.unroll()
    assert len(swap_space) == 18
    assert circuit in swap_space
    circuit.x(2).mcx([1, 2], 0).x(1)
    circuit.x(2).x(1).mcx([1, 2], 0)
    circuit.x(0).mcx([0, 1], 2).x(1)

    circuit = Circuit(2)
    circuit.cx(0, 1).x(0).cx(0, 1).x(0).x(1)
    swap_space = circuit.unroll()
    assert len(swap_space) == 20
    assert circuit in swap_space
    circuit.cx(0, 1).x(0).x(1).cx(0, 1).x(0)
    circuit.cx(1, 0).x(1).cx(1, 0).x(1).x(0)
    circuit.cx(0, 1).x(0).cx(0, 1).x(0).x(1)
    circuit.x(1).x(0).cx(0, 1).x(0).cx(0, 1)

    circuit = Circuit(3)
    circuit.cx(1, 2).cx(0, 1).cx(1, 2).cx(0, 2).cx(0, 1)
    swap_space = circuit.unroll()
    assert len(swap_space) == 60
    assert circuit in swap_space

    circuit = Circuit(3)
    circuit.cx(0, 2).mcx([0, 1], 2).x(1).mcx([0, 1], 2).x(1)
    swap_space = circuit.unroll()
    assert len(swap_space) == 60
    assert circuit in swap_space
