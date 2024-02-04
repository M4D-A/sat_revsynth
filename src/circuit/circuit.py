from ..truth_table.truth_table import TruthTable
from ..utils.inplace import inplace
from copy import copy, deepcopy

Gate = tuple[list[int], int]  # Gate in integer representation


class Circuit:
    def __init__(self, bits_num: int):
        self._width = bits_num
        self._tt = TruthTable(bits_num)
        self._gates: list[Gate] = []

    def width(self) -> int:
        return self._width

    def tt(self) -> TruthTable:
        return self._tt

    def gates(self) -> list[Gate]:
        return self._gates

    def __copy__(self) -> "Circuit":
        new = Circuit(self._width)
        new._tt = copy(self._tt)
        new._gates = deepcopy(self._gates)
        return new

    def __str__(self) -> str:
        header = f"width = {self._width} gates_num = {len(self._gates)}\n"
        gates = ""
        for controls, target in self._gates:
            gates += f"{str(controls)} -> {target}\n"
        tt = f"{self._tt}"
        return header + gates + tt

    def __len__(self) -> int:
        return len(self._gates)

    def __eq__(self, other) -> bool:
        return (self._width, self._tt, self._gates) == (other._width, other._tt, other._gates)

    def __add__(self, other) -> "Circuit":
        assert self._width == other._width
        new_width = self._width
        new_circuit = Circuit(new_width)
        new_circuit._gates = self._gates + other._gates
        new_circuit._tt = self._tt + other._tt
        return new_circuit

    @inplace
    def x(self, target: int, **_) -> "Circuit":
        assert 0 <= target and target < self._width
        self._gates.append(([], target))
        self._tt.x(target)
        return self

    @inplace
    def cx(self, control: int, target: int, **_) -> "Circuit":
        assert 0 <= target and target < self._width
        assert 0 <= control and control < self._width
        self._gates.append(([control], target))
        self._tt.cx(control, target)
        return self

    @inplace
    def mcx(self, controls: list[int], target: int, **_) -> "Circuit":
        assert 0 <= target and target < self._width
        assert all([0 <= cid and cid < self._width for cid in controls])
        controls = sorted(controls)
        self._gates.append((controls, target))
        self._tt.mcx(controls, target)
        return self

    @inplace
    def append(self, gate, **_) -> "Circuit":
        controls, target = gate
        self.mcx(controls, target)
        return self

    @inplace
    def pop(self, **_) -> "Circuit":
        controls, target = self._gates[-1]
        self._tt.mcx(controls, target)
        self._gates.pop()
        return self

    @inplace
    def reverse(self, **_) -> "Circuit":
        self._tt.inverse(inplace=True)
        self._gates.reverse()
        return self

    @inplace
    def rotate(self, shift: int, **_) -> "Circuit":
        size = len(self)
        shift = (shift % size) + size % size
        gates = self._gates
        new_gates = gates[shift:] + gates[:shift]
        new_tt = TruthTable(self._width)
        for gate in new_gates:
            new_tt.mcx(*gate)
        self._gates = new_gates
        self._tt = new_tt
        return self

    @inplace
    def permute(self, permutation: list[int], **_) -> "Circuit":
        new_gates: list[Gate] = []
        for controls, target in self._gates:
            new_target = permutation[target]
            new_controls = sorted([permutation[c] for c in controls])
            new_gates.append((new_controls, new_target))
        self._gates = new_gates
        self._tt.permute(permutation, permute_input=True, inplace=True)
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
