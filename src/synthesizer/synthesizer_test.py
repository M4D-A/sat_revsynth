import pytest
from random import randint, sample
from itertools import product
from functools import reduce
from copy import deepcopy
from sat.solver import Solver
from truth_table.truth_table import TruthTable
from synthesizer.synthesizer import Synthesizer

solver_names = Solver.builtin_solvers.keys()
solvers = [Solver(solver_name) for solver_name in solver_names]
max_bits_size = 8
epochs = 2**3
bits_num_randomizer = list(randint(3, max_bits_size) for _ in range(epochs))


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
def identity_tt(bits_num):
    return TruthTable(bits_num)


@pytest.mark.parametrize("solver", solvers)
@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_empty(solver, identity_tt):
    synthesizer = Synthesizer(identity_tt, 0, solver)
    circuit = synthesizer.solve()
    assert circuit is not None
    assert len(circuit) == 0
    assert circuit.tt() == identity_tt


@pytest.mark.parametrize("solver", solvers)
@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_single_x(solver, identity_tt, x_params):
    tt = identity_tt.x(x_params, inplace=False)
    synthesizer = Synthesizer(tt, 1, solver)
    circuit = synthesizer.solve()
    assert circuit is not None
    assert len(circuit) == 1
    assert circuit.tt() == tt
    controls, target = circuit[0]
    assert controls == []
    assert target == x_params


@pytest.mark.parametrize("solver", solvers)
@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_single_cx(solver, identity_tt, cx_params):
    tt = identity_tt.cx(*cx_params, inplace=False)
    synthesizer = Synthesizer(tt, 1, solver)
    circuit = synthesizer.solve()
    assert circuit is not None
    assert len(circuit) == 1
    assert circuit.tt() == tt
    controls, target = circuit[0]
    assert controls == [cx_params[0]]
    assert target == cx_params[1]


@pytest.mark.parametrize("solver", solvers)
@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_single_mcx(solver, identity_tt, mcx_params):
    tt = identity_tt.mcx(*mcx_params, inplace=False)
    synthesizer = Synthesizer(tt, 1, solver)
    circuit = synthesizer.solve()
    assert circuit is not None
    assert len(circuit) == 1
    assert circuit.tt() == tt
    controls, target = circuit[0]
    assert controls == sorted(mcx_params[0])
    assert target == mcx_params[1]
