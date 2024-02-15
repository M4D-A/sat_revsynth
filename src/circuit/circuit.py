from warnings import catch_warnings, filterwarnings
with catch_warnings():
    filterwarnings("ignore", category=DeprecationWarning)
    from qiskit import QuantumCircuit
from copy import copy, deepcopy
from itertools import permutations
from functools import reduce
from truth_table.truth_table import TruthTable
from utils.inplace import inplace
from collections import deque

Gate = tuple[list[int], int]  # Gate in integer representation


class Circuit:
    def __init__(self, bits_num: int):
        self._width = bits_num
        self._tt: TruthTable | None = None
        self._gates: list[Gate] = []
        self._exclusion_list: None | list[int] = None

    def width(self) -> int:
        return self._width

    def tt(self) -> TruthTable:
        if self._tt is None:
            self._tt = TruthTable(self._width)
            for controls, target in self._gates:
                self._tt.mcx(controls, target)
        return self._tt

    def gates(self) -> list[Gate]:
        return self._gates

    def controls_num(self) -> int:
        return reduce(lambda x, y: x + len(y[0]), self._gates, 0)

    def __copy__(self) -> "Circuit":
        new = Circuit(self._width)
        new._tt = copy(self._tt)
        new._gates = deepcopy(self._gates)
        return new

    def __str__(self) -> str:
        qc = QuantumCircuit(self._width)
        for controls, target in self._gates:
            if len(controls) == 0:
                qc.x(target)
            else:
                qc.mcx(controls, target)
            qc.barrier()
        return str(qc.draw(justify="none", plot_barriers=False, output="text"))

    def __len__(self) -> int:
        return len(self._gates)

    def __eq__(self, other) -> bool:
        return (self._width, self._gates) == (other._width, other._gates)

    def __add__(self, other) -> "Circuit":
        assert self._width == other._width
        new_width = self._width
        new_circuit = Circuit(new_width)
        new_circuit._gates = self._gates + other._gates
        return new_circuit

    def __getitem__(self, id) -> Gate:
        return self._gates[id]

    @classmethod
    def filter_duplicates(cls, unfiltered: list["Circuit"]) -> list["Circuit"]:
        return [circ for i, circ in enumerate(unfiltered) if circ not in unfiltered[:i]]

    @inplace
    def x(self, target: int, **_) -> "Circuit":
        assert 0 <= target and target < self._width
        self._gates.append(([], target))
        self._tt = None
        return self

    @inplace
    def cx(self, control: int, target: int, **_) -> "Circuit":
        assert 0 <= target and target < self._width
        assert 0 <= control and control < self._width
        self._gates.append(([control], target))
        self._tt = None
        return self

    @inplace
    def mcx(self, controls: list[int], target: int, **_) -> "Circuit":
        assert 0 <= target and target < self._width
        assert all([0 <= cid and cid < self._width for cid in controls])
        controls = sorted(controls)
        self._gates.append((controls, target))
        self._tt = None
        return self

    @inplace
    def append(self, gate, **_) -> "Circuit":
        controls, target = gate
        self.mcx(controls, target)
        self._tt = None
        return self

    @inplace
    def pop(self, **_) -> "Circuit":
        self._gates.pop()
        self._tt = None
        return self

    def reverse(self) -> "Circuit":
        new = Circuit(self._width)
        new._gates = deepcopy(self._gates)
        new._gates.reverse()
        return new

    def rotate(self, shift: int) -> "Circuit":
        size = len(self)
        shift = (shift % size) + size % size
        new = Circuit(self._width)
        new._gates = deepcopy(self._gates)
        new._gates = new._gates[shift:] + new._gates[:shift]
        return new

    def permute(self, permutation: list[int]) -> "Circuit":
        new_gates: list[Gate] = []
        for controls, target in self._gates:
            new_target = permutation[target]
            new_controls = sorted([permutation[c] for c in controls])
            new_gates.append((new_controls, new_target))
        new = Circuit(self._width)
        new._gates = new_gates
        return new

    def swap(self, id: int) -> "Circuit":
        assert 0 <= id and id < len(self)
        next_id = (id + 1) % len(self)
        new = Circuit(self._width)
        new._gates = deepcopy(self._gates)
        new._gates[id], new._gates[next_id] = new._gates[next_id], new._gates[id]
        return new

    def rotations(self) -> list["Circuit"]:
        equivalents = [self.rotate(s) for s in range(len(self))]
        unique = self.filter_duplicates(equivalents)
        return unique

    def permutations(self) -> list["Circuit"]:
        all_permutations = permutations(list(range(self._width)))
        equivalents = [self.permute(list(perm)) for perm in all_permutations]
        unique = self.filter_duplicates(equivalents)
        return unique

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

    def swaps(self) -> list["Circuit"]:
        swap_ids = self.swappable_gates()
        equivalents = [copy(self)] + [self.swap(id) for id in swap_ids]
        unique = self.filter_duplicates(equivalents)
        return unique

    def _dfs(self, visited: list["Circuit"]):
        visited.append(self)
        neighbours = self.swaps()
        for node in neighbours:
            if not (node in visited):
                node._dfs(visited)

    def swap_space_dfs(self) -> list["Circuit"]:
        nodes = []
        self._dfs(nodes)
        return nodes

    def swap_space_bfs(self, initial: list["Circuit"] = []) -> list["Circuit"]:
        visited: list["Circuit"] = []
        queue: deque["Circuit"] = deque()
        queue.append(self)
        for other in initial:
            if other not in initial:
                queue.append(other)

        while queue:
            curr = queue.popleft()

            if curr not in visited:
                visited.append(curr)

                for neighbor in curr.swaps():
                    if neighbor not in visited:
                        queue.append(neighbor)
        return visited

    def local_unroll(self) -> list["Circuit"]:
        equivalents = self.rotations()

        temp_list = [circuit.reverse() for circuit in equivalents]
        equivalents += temp_list

        temp_list = []
        for circuit in equivalents:
            temp_list += circuit.permutations()
        equivalents = temp_list

        return equivalents

    def unroll(self, initial: list["Circuit"] = []) -> list["Circuit"]:
        equivalents = self.swap_space_bfs(initial)

        temp_list = []
        for circuit in equivalents:
            rotations = circuit.rotations()
            temp_list += rotations
        equivalents = temp_list

        temp_list = [circuit.reverse() for circuit in equivalents]
        equivalents += temp_list
        equivalents = self.filter_duplicates(equivalents)

        temp_list = []
        for circuit in equivalents:
            temp_list += circuit.permutations()
        equivalents = temp_list

        unique = self.filter_duplicates(equivalents)
        return unique
