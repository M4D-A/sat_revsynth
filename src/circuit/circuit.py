from ..truth_table.truth_table import TruthTable
from ..utils.inplace import inplace
from copy import copy, deepcopy

Gate = tuple[list[int], int]  # Gate in integer representation


class Circuit:
    def __init__(self, bits_num: int):
        self._width = bits_num
        self._tt = TruthTable(bits_num)
        self._gates: list[Gate] = []

    def width(self):
        return self._width

    def tt(self):
        return self._tt

    def gates(self):
        return self._gates

    @inplace
    def x(self, target: int, **_):
        assert 0 <= target and target < self._width
        self._gates.append(([], target))
        self._tt.x(target)
        return self

    @inplace
    def cx(self, control: int, target: int, **_):
        assert 0 <= target and target < self._width
        assert 0 <= control and control < self._width
        self._gates.append(([control], target))
        self._tt.cx(control, target)
        return self

    @inplace
    def mcx(self, controls: list[int], target: int, **_):
        assert 0 <= target and target < self._width
        assert all([0 <= cid and cid < self._width for cid in controls])
        controls = sorted(controls)
        self._gates.append((controls, target))
        self._tt.mcx(controls, target)
        return self

    @inplace
    def append(self, gate, **_):
        controls, target = gate
        self.mcx(controls, target)
        return self

    def gate_swappable(self, index, ignore_identical: bool = True) -> bool:
        lhs = self._gates[index]
        rhs = self._gates[(index + 1) % len(self)]
        if ignore_identical and lhs == rhs:
            return False
        lhs_controls, lhs_target = lhs
        rhs_controls, rhs_target = rhs
        lhs_collision = lhs_target in rhs_controls
        rhs_collision = rhs_target in lhs_controls
        return not (lhs_collision) and not (rhs_collision)

    def swappable_gates(self, ignore_identical: bool = True) -> list[int]:
        indices = [i for i in range(len(self)) if self.gate_swappable(i, ignore_identical)]
        return indices

    def __copy__(self):
        new = Circuit(self._width)
        new._tt = copy(self._tt)
        new._gates = deepcopy(self._gates)
        return new

    def __len__(self):
        return len(self._gates)

    def __eq__(self, other):
        return (self._width, self._tt, self._gates) == (other.width, other.tt, other.gates)

    def __add__(self, other):
        assert self._width == other._width
        new_width = self._width
        new_circuit = Circuit(new_width)
        new_circuit._gates = self._gates + other._gates
        new_circuit._tt = self._tt + other._tt
