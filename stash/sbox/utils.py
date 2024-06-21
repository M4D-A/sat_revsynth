from functools import cache
from itertools import product
from random import sample


def random_table(n, k):
    table = [0] * n
    positions = sample(range(n), k)
    for pos in positions:
        table[pos] = 1
    return table


def is_power_of_two(n: int) -> bool:
    return (n & (n - 1) == 0) and n != 0


def is_permutation(table: list[int]) -> bool:
    exists = [0] * len(table)
    for elem in table:
        if elem < 0 or elem >= len(table):
            return False
        exists[elem] = 1
    return all(exists)


def is_bit_table(table: list[int]) -> bool:
    return all(e in [0, 1] for e in table)


def xor_tables(lhs_table: list[int], rhs_table: list[int]):
    return [lhs ^ rhs for lhs, rhs in zip(lhs_table, rhs_table)]


def monomial_function(bits_num: int, variable_id: int):
    assert bits_num > 0
    assert 0 <= variable_id and variable_id < bits_num

    table_size = pow(2, bits_num)
    block_size = pow(2, variable_id)
    blocks_num = table_size // block_size
    return ([0] * block_size + [1] * block_size) * (blocks_num // 2)


def monomial_complementary_function(bits_num: int, variable_id: int):
    assert bits_num > 0
    assert 0 <= variable_id and variable_id < bits_num

    table_size = pow(2, bits_num)
    block_size = pow(2, variable_id)
    blocks_num = table_size // block_size
    return ([0] * block_size + [1] * block_size) * (blocks_num // 2)


def pascal_transform(table: list[int], lhs: int = 0, rhs: int | None = None) -> list[int]:
    assert is_power_of_two(len(table))
    assert is_bit_table(table)

    if rhs is None:
        rhs = len(table)
    size = rhs - lhs
    mid = lhs + (size // 2)

    if size > 1:
        pascal_transform(table, lhs, mid)
        pascal_transform(table, mid, rhs)
        for i in range(lhs, mid):
            table[i + size // 2] ^= table[i]
    return table


def algebraic_degree(table: list[int]) -> int:
    assert is_power_of_two(len(table))
    assert is_bit_table(table)

    spectra = pascal_transform(table[:])

    degree = 0
    for term, coefficient in enumerate(spectra):
        if coefficient:
            term_degree = term.bit_count()
            degree = max(degree, term_degree)
    return degree


@cache
def get_affine_functions(n) -> list[list[int]]:
    coefficients = list(product([0, 1], repeat=n + 1))

    def affine_function(coeffs, x):
        result = coeffs[0]  # Start with a_0
        for i in range(n):
            result ^= coeffs[i + 1] & x[i]  # XOR with a_i * x_i
        return result

    affine_functions = []
    for coeffs in coefficients:
        output_bits = []
        for x in product([0, 1], repeat=n):
            output_bits.append(affine_function(coeffs, x))
        affine_functions.append(output_bits)

    return affine_functions


def hamming_distance(lhs_table: list[int], rhs_table: list[int]) -> int:
    return sum(lhs == rhs for lhs, rhs in zip(lhs_table, rhs_table))
