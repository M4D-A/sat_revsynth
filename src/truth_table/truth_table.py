from collections.abc import Iterable
from random import shuffle
from ..utils.inplace import inplace
from copy import copy


class TruthTable:
    def __init__(self, bits_num: int,
                 values: list[int] | None = None,
                 bits: list[list[int]] | None = None,
                 ):
        rows_num = 2 ** bits_num
        assert values is None or bits is None

        if bits is None:
            values = list(range(rows_num)) if values is None else values
            assert len(values) == rows_num
            bits = [self.value_to_row(row, bits_num) for row in values]
        else:
            assert len(bits) == rows_num
            assert all(len(row) == bits_num for row in bits)

        self._bits = bits
        self._bits_num = bits_num

    def __copy__(self):
        return TruthTable(self._bits_num, bits=[copy(row) for row in self.bits()])

    def __eq__(self, other):
        lhs = (self._bits_num, self._bits)
        rhs = (other._bits_num, other._bits)
        return lhs == rhs

    def __len__(self):
        return len(self._bits)

    def __add__(self, other):
        assert len(self) == len(other)
        new_values = [other.values()[v] for v in self.values()]
        return TruthTable(self._bits_num, new_values)

    def __str__(self):
        header = f"bits = {self._bits_num}, rows = {len(self)}\n\n"
        rows = "\n".join([str(i) + ": " + str(row) for i, row in zip(self.values(), self._bits)])
        return header + rows

    @classmethod
    def row_to_value(cls, row: list[int]) -> int:
        value = 0
        for i, b in enumerate(row):
            value += 2**i * b
        return value

    @classmethod
    def value_to_row(cls, value: int, bits_num: int) -> list[int]:
        return [(value >> s) & 1 for s in range(bits_num)]

    def values(self):
        return [self.row_to_value(row) for row in self._bits]

    def bits_num(self):
        return self._bits_num

    def bits(self):
        return self._bits

    @ inplace
    def x(self, target: int, **_):
        for row in self._bits:
            row[target] = 1 - row[target]
        return self

    @ inplace
    def cx(self, control: int, target: int, **_) -> "TruthTable":
        for row in self._bits:
            if row[control] == 1:
                row[target] = 1 - row[target]
        return self

    @ inplace
    def mcx(self, controls: Iterable[int], target: int, **_) -> "TruthTable":
        for row in self._bits:
            if all([row[control] == 1 for control in controls]):
                row[target] = 1 - row[target]
        return self

    @ inplace
    def shuffle(self, **_) -> "TruthTable":
        assert self._bits is not None
        new_bits = [copy(row) for row in self.bits()]
        shuffle(new_bits)
        self._bits = new_bits
        return self
