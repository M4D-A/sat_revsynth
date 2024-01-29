from collections.abc import Sequence, Iterable
from random import shuffle


class TruthTable:
    def __init__(self, bits_num: int, values: Sequence[int] | None = None):
        if values is None:
            values = range(pow(2, bits_num))
        else:
            assert len(values) == pow(2, bits_num)

        self._bits_num = bits_num
        self._values = list(values)
        self._bits = [[(i >> s) & 1 for s in range(bits_num)] for i in values]

    def __eq__(self, other):
        lhs = (self._bits_num, self._values, self._bits)
        rhs = (other._bits_num, other._values, other._bits)
        return lhs == rhs

    def __len__(self):
        return len(self._values)

    def __add__(self, other):
        assert len(self) == len(other)
        new_values = [other.values()[v] for v in self.values()]
        return TruthTable(self._bits_num, new_values)

    def __str__(self):
        header = f"bits = {self.bits_num()}, rows = {len(self)}\n\n"
        rows = "\n".join([str(row) for row in self.bits()])
        return header + rows

    def values(self):
        return self._values

    def bits_num(self):
        return self._bits_num

    def bits(self):
        return self._bits

    def x(self, target: int, inplace: bool = True) -> "TruthTable":
        if inplace:
            for row in self._bits:
                row[target] = 1 - row[target]
            return self
        else:
            new_tt = TruthTable(self._bits_num)
            return new_tt.x(target, True)

    def cx(self, control: int, target: int, inplace: bool = True) -> "TruthTable":
        if inplace:
            for row in self._bits:
                if row[control] == 1:
                    row[target] = 1 - row[target]
            return self
        else:
            new_tt = TruthTable(self._bits_num)
            return new_tt.cx(control, target, True)

    def mcx(self, controls: Iterable[int], target: int, inplace: bool = True) -> "TruthTable":
        if inplace:
            for row in self._bits:
                if all([row[control] == 1 for control in controls]):
                    row[target] = 1 - row[target]
            return self
        else:
            new_tt = TruthTable(self._bits_num)
            return new_tt.mcx(controls, target, True)

    def shuffle(self):
        reordering = self.values().copy()
        shuffle(reordering)
        new_bits = [self._bits[i] for i in reordering]
        new_values = [self._values[i] for i in reordering]
        self._bits = new_bits
        self._values = new_values
        return self
