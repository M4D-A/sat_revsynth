import pytest
from random import randint, sample
from copy import copy
from .truth_table import TruthTable


max_bits_size = 8
epochs = 2**8
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
def random_tt(bits_num):
    return TruthTable(bits_num).shuffle()


@pytest.fixture
def identity_tt(bits_num):
    return TruthTable(bits_num)


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_x(x_params, random_tt):
    tt = copy(random_tt)
    target = x_params
    tt.x(target)
    for ref_row, row in zip(random_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_cx(cx_params, random_tt):
    tt = copy(random_tt)
    control, target = cx_params
    tt.cx(control, target)
    for ref_row, row in zip(random_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and row[control] == 1:
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_mcx(mcx_params, random_tt):
    tt = copy(random_tt)
    controls, target = mcx_params
    tt.mcx(controls, target)
    for ref_row, row in zip(random_tt.bits(), tt.bits()):
        for i, (ref_b, b) in enumerate(zip(ref_row, row)):
            if i == target and all(row[c] for c in controls):
                assert ref_b != b
            else:
                assert ref_b == b


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_x_involutivity(x_params, random_tt):
    tt = copy(random_tt)
    target = x_params
    tt.x(target)
    tt.x(target)
    assert tt == random_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_cx_involutivity(cx_params, random_tt):
    tt = copy(random_tt)
    control, target = cx_params
    tt.cx(control, target)
    tt.cx(control, target)
    assert tt == random_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_mcx_involutivity(mcx_params, random_tt):
    tt = copy(random_tt)
    controls, target = mcx_params
    tt.mcx(controls, target)
    tt.mcx(controls, target)
    assert tt == random_tt


@pytest.mark.parametrize("bits_num", bits_num_randomizer)
def test_inplace(x_params, identity_tt):
    tt_a = copy(identity_tt)
    target = x_params

    tt_b = tt_a.x(target, inplace=False)
    assert tt_a == identity_tt
    assert tt_b != identity_tt

    tt_a.x(target, inplace=True)
    assert tt_a != identity_tt
    assert tt_b != identity_tt
    assert tt_b == tt_a

    tt_a.x(target)
    tt_b.x(target)
    assert tt_a == identity_tt
    assert tt_b == identity_tt
    assert tt_b == tt_a
