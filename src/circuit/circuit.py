from ..truth_tables import TruthTable
from qiskit import QuantumCircuit

Gate = tuple[list[int], int]  # Gate in integer representation


class Circuit:
    def __init__(self, bits_num: int):
        self.width = bits_num
        self.tt = TruthTable(bits_num)
        self.gates: list[Gate] = []

    def x(self, target: int):
        assert 0 <= target and target < self.width
        self.gates.append(([], target))
        self.tt.nott(target)
        return self

    def mcx(self, controls: list[int], target: int):
        assert 0 <= target and target < self.width
        assert all([0 <= cid and cid < self.width for cid in controls])
        controls = sorted(controls)
        self.gates.append((controls, target))
        self.tt.mcnot(controls, target)
        return self

    def append(self, gate):
        controls, target = gate
        self.mcx(controls, target)

    def __len__(self):
        return len(self.gates)

    def __eq__(self, other):
        return (self.width, self.tt, self.gates) == (other.width, other.tt, other.gates)

    def print(self):
        qc = QuantumCircuit(self.width)
        for controls, target in self.gates:
            if len(controls) == 0:
                qc.x(target)
            else:
                qc.mcx(controls, target)
            qc.barrier()
        print(qc.draw(justify="none", plot_barriers=False))
