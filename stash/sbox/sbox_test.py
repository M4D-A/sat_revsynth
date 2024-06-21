import pytest
from .utils import (
    algebraic_degree,
    monomial_complementary_function,
    xor_tables,
    monomial_function,
)


max_bits_size = 8
epochs = 2**6
bits_num_range = [b for b in range(1, max_bits_size + 1)]
bits_num_variable_range = [(b, v) for b in bits_num_range for v in range(0, b)]


@pytest.mark.parametrize("bits_num", bits_num_range)
def test_constant_functions(bits_num):
    table = [0] * pow(2, bits_num)
    assert algebraic_degree(table) == 0

    table = [1] * pow(2, bits_num)
    assert algebraic_degree(table) == 0


@pytest.mark.parametrize("bits_num, variable_id", bits_num_variable_range)
def test_monomial_functions(bits_num, variable_id):
    table = monomial_function(bits_num, variable_id)
    assert algebraic_degree(table) == 1

    table = monomial_complementary_function(bits_num, variable_id)
    assert algebraic_degree(table) == 1


@pytest.mark.parametrize("bits_num", bits_num_range)
def test_linear_functions(bits_num):

    table_size = pow(2, bits_num)
    acc_table = [0] * table_size

    for var in range(0, bits_num):
        block_size = pow(2, var)
        blocks_num = table_size // block_size
        table = ([0] * block_size + [1] * block_size) * (blocks_num // 2)
        acc_table = xor_tables(acc_table, table)
        assert algebraic_degree(acc_table) == 1

    for var in range(0, bits_num - 1):
        block_size = pow(2, var)
        blocks_num = table_size // block_size
        table = ([0] * block_size + [1] * block_size) * (blocks_num // 2)
        acc_table = xor_tables(acc_table, table)
        assert algebraic_degree(acc_table) == 1


# def test_max_degree_functions():
#     for _ in range(EPOCHS):
#         for bits in range(1, MAX_BITS):
#             table_size = pow(2, bits)
#             random_odd = 2 * random.randint(1, table_size // 2) - 1
#             table = random_table(table_size, random_odd)
#             assert algebraic_degree(table) == bits
#
#
# def test_submax_degree_nonconst_functions():
#     for _ in range(EPOCHS):
#         for bits in range(2, MAX_BITS):
#             table_size = pow(2, bits)
#             table_size = pow(2, bits)
#             random_even = 2 * random.randint(1, table_size // 2 - 1)
#             table = random_table(table_size, random_even)
#             degree = algebraic_degree(table)
#             assert 0 < degree and degree < bits
