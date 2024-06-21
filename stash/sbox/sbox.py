from sbox.utils import (
    pascal_transform,
    get_affine_functions,
    hamming_distance,
    is_power_of_two,
    is_permutation,
)


class Sbox:

    def __init__(self, bits: int, table: list[int] | None = None):

        def _check_table(table: list[int]) -> bool:
            power_of_two_size = is_power_of_two(len(table))
            return power_of_two_size and is_permutation(table)

        size = pow(2, bits)

        if table is not None:
            assert len(table) == size
            assert _check_table(table)
        else:
            table = list(range(size))

        self._bits = bits
        self._table = table

    def bits(self) -> int:
        return self._bits

    def table(self) -> list[int]:
        return self._table

    def partial_table(self, k: int) -> list[int]:
        assert 0 <= k and k <= self._bits
        return [(elem >> k) & 1 for elem in self._table]

    def algebraic_degree(self) -> int:
        spectra = pascal_transform(self._table[:])
        degree = 0
        for term, coefficient in enumerate(spectra):
            if coefficient:
                term_degree = term.bit_count()
                degree = max(degree, term_degree)

        return degree

    def nonlinearity_degree(self) -> int:
        af_functions = get_affine_functions(self._bits)
        partial = self.partial_table(0)
        return min(hamming_distance(partial, af) for af in af_functions)
