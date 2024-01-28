from ..truth_tables import TruthTable
from qiskit import QuantumCircuit

Gate = tuple[list[int], int]  # Gate in integer representation


class Circuit:
    def __init__(self, bits_num: int):
        self._width = bits_num
        self._tt = TruthTable(bits_num)
        self._gates: list[Gate] = []

    def x(self, target: int):
        assert 0 <= target and target < self._width
        self._gates.append(([], target))
        self._tt.nott(target)
        return self

    def mcx(self, controls: list[int], target: int):
        assert 0 <= target and target < self._width
        assert all([0 <= cid and cid < self._width for cid in controls])
        controls = sorted(controls)
        self._gates.append((controls, target))
        self._tt.mcnot(controls, target)
        return self

    def append(self, gate):
        controls, target = gate
        self.mcx(controls, target)

    def is_swappable(self, index, ignore_identical: bool = True) -> bool:
        lhs = self._gates[index]
        rhs = self._gates[index + 1]
        if ignore_identical and lhs == rhs:
            return False
        lhs_controls, lhs_target = lhs
        rhs_controls, rhs_target = rhs
        lhs_collision = lhs_target in rhs_controls
        rhs_collision = rhs_target in lhs_controls
        return not (lhs_collision) and not (rhs_collision)

    def __len__(self):
        return len(self._gates)

    def __eq__(self, other):
        return (self._width, self._tt, self._gates) == (other.width, other.tt, other.gates)

    def print(self):
        qc = QuantumCircuit(self._width)
        for controls, target in self._gates:
            if len(controls) == 0:
                qc.x(target)
            else:
                qc.mcx(controls, target)
            qc.barrier()
        print(qc.draw(justify="none", plot_barriers=False))
