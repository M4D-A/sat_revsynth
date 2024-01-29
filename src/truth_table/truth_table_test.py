import pytest
from random import randint, sample
from .truth_table import TruthTable

max_tt_size = 8
epochs = 10000
size_randomizer = list(randint(3, max_tt_size) for _ in range(epochs))


@pytest.mark.parametrize("tt_size", size_randomizer)
# @pytest.mark.parametrize("tt_size", [3])
def test_inplace(tt_size):
    tt_a = TruthTable(tt_size)
    target = randint(0, tt_size - 1)

    tt_b = tt_a.x(target, inplace=False)
    assert tt_a == TruthTable(tt_size)
    assert tt_b != TruthTable(tt_size)

    tt_a.x(target, inplace=True)
    assert tt_a != TruthTable(tt_size)
    assert tt_b != TruthTable(tt_size)
    assert tt_b == tt_a

    tt_c = tt_b.x(target, inplace=False)
    tt_b.x(target, inplace=True)
    tt_a.x(target, inplace=True)
    assert tt_a == TruthTable(tt_size)
    assert tt_b == TruthTable(tt_size)
    assert tt_c == TruthTable(tt_size)

#
# @pytest.mark.parametrize("tt_size", size_randomizer)
# def test_x(tt_size):
#     ref_tt = TruthTable(tt_size).shuffle()
#     tt = deepcopy(ref_tt)
#     target = randint(0, tt.bits_num() - 1)
#     tt.x(target)
#     for ref_row, row in zip(ref_tt.bits(), tt.bits()):
#         for i, (ref_b, b) in enumerate(zip(ref_row, row)):
#             if i == target:
#                 assert ref_b != b
#             else:
#                 assert ref_b == b
#
#
# @pytest.mark.parametrize("tt_size", size_randomizer)
# def test_cx(tt_size):
#     ref_tt = TruthTable(tt_size).shuffle()
#     tt = deepcopy(ref_tt)
#     control, target = sample(range(0, tt.bits_num() - 1), 2)
#     tt.cx(control, target)
#     for ref_row, row in zip(ref_tt.bits(), tt.bits()):
#         for i, (ref_b, b) in enumerate(zip(ref_row, row)):
#             if i == target and row[control] == 1:
#                 assert ref_b != b
#             else:
#                 assert ref_b == b
#
#
# @pytest.mark.parametrize("tt_size", size_randomizer)
# def test_mcx(tt_size):
#     ref_tt = TruthTable(tt_size).shuffle()
#     tt = deepcopy(ref_tt)
#     special_ids_num = randint(2, tt.bits_num() - 1)
#     target, *controls = sample(range(0, tt.bits_num() - 1), special_ids_num)
#     tt.mcx(controls, target)
#     for ref_row, row in zip(ref_tt.bits(), tt.bits()):
#         for i, (ref_b, b) in enumerate(zip(ref_row, row)):
#             if i == target and all(row[c] for c in controls):
#                 assert ref_b != b
#             else:
#                 assert ref_b == b
#
#
# @pytest.mark.parametrize("tt_size", size_randomizer)
# def test_x_involutivity(tt_size):
#     ref_tt = TruthTable(tt_size).shuffle()
#     tt = deepcopy(ref_tt)
#     target = randint(0, tt.bits_num() - 1)
#     tt.x(target)
#     tt.x(target)
#     assert tt == ref_tt
#
#
# @pytest.mark.parametrize("tt_size", size_randomizer)
# def test_cx_involutivity(tt_size):
#     ref_tt = TruthTable(tt_size).shuffle()
#     tt = deepcopy(ref_tt)
#     control, target = sample(range(0, tt.bits_num() - 1), 2)
#     tt.cx(control, target)
#     tt.cx(control, target)
#     assert tt == ref_tt
#
#
# @pytest.mark.parametrize("tt_size", size_randomizer)
# def test_mcx_involutivity(tt_size):
#     ref_tt = TruthTable(tt_size).shuffle()
#     tt = deepcopy(ref_tt)
#     special_ids_num = randint(2, tt.bits_num() - 1)
#     target, *controls = sample(range(0, tt.bits_num() - 1), special_ids_num)
#     tt.mcx(controls, target)
#     tt.mcx(controls, target)
#     assert tt == ref_tt
