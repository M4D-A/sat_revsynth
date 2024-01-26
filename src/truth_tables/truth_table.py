from collections.abc import Sequence, Iterable


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

    def values(self):
        return self._values

    def bits_num(self):
        return self._bits_num

    def nott(self, target: int, inplace: bool = True) -> "TruthTable":
        if inplace:
            for row in self._bits:
                row[target] = 1 - row[target]
            return self
        else:
            new_tt = TruthTable(self._bits_num)
            return new_tt.nott(target, True)

    def cnot(self, control: int, target: int,
             inplace: bool = True) -> "TruthTable":
        if inplace:
            for row in self._bits:
                if row[control] == 1:
                    row[target] = 1 - row[target]
            return self
        else:
            new_tt = TruthTable(self._bits_num)
            return new_tt.cnot(control, target, True)

    def mcnot(self, controls: Iterable[int], target: int,
              inplace: bool = True) -> "TruthTable":
        if inplace:
            for row in self._bits:
                if all([row[control] == 1 for control in controls]):
                    row[target] = 1 - row[target]
            return self
        else:
            new_tt = TruthTable(self._bits_num)
            return new_tt.mcnot(controls, target, True)