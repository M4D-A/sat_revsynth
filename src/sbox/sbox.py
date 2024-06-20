class Sbox:

    @staticmethod
    def _is_power_of_two(n: int):
        return (n & (n-1) == 0) and n != 0

    @staticmethod
    def _is_permutation(table: list[int]):
        exists = [0] * len(table)
        for elem in table:
            if elem < 0 or elem >= len(table):
                return False
            exists[elem] = 1
        return all(exists)

    @staticmethod
    def _check_table(table: list[int]) -> bool:
        power_of_two_size = Sbox._is_power_of_two(len(table))
        return power_of_two_size and Sbox._is_permutation(table)

    def __init__(self, bits: int, table: list[int] | None = None):
        size = pow(2, bits) 

        if table is not None:
            assert len(table) == size
            assert Sbox._check_table(table)
        else:
            table = list(range(size))

        self._bits = bits
        self._table = table

    def bits(self) -> int:
        return self._bits

    def table(self) -> list[int]:
        return self._table

    def algebraic_degree(self) -> int:
        def _pascal_transform(function: list[int], left: int = 0, right: int | None = None): 
            if right is None:
                right = len(function)
            size = right - left
            mid = left + (size // 2)

            if size > 1:
                _pascal_transform(function, left, mid)
                _pascal_transform(function, mid, right)
                for i in range(left, mid):
                    function[i + size//2] ^= function[i] 
            return function

        spectra = _pascal_transform(self._table[:])

        degree = 0
        for term, coefficient in enumerate(spectra):
            if coefficient:
                term_degree = term.bit_count()
                degree = max(degree, term_degree)

        return degree

