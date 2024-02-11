from circuit.circuit import Circuit
from truth_table.truth_table import TruthTable
from sat.cnf import CNF
from sat.solver import Solver
from itertools import product
from functools import reduce

# max_controls: int | None = None,
# ancilla_num: int = 0,
# max_clauses_len: int = 3,
# encoding: int = 1,
# solver: solver = solver("cadical")
# assert max_controls is None or max_controls >= 0
# assert ancilla_num >= 0
# assert max_clauses_len >= 3


class Synthesizer:
    def __init__(self,
                 output: TruthTable,
                 gate_count: int,
                 solver: Solver,
                 **kwargs
                 ):
        assert len(output) >= 2
        assert len(output) == pow(2, len(output[0]))
        assert all(len(word) == len(output[0]) for word in output)
        assert gate_count >= 0

        self._output = output
        self._gate_count = gate_count
        self._solver = solver
        self._width = len(output[0])
        self._words = len(output)
        # self.ancilla_num = ancilla_num
        self._max_clauses_len = 3
        self._encoding = 1
        # self.solution = None
        # self.circuit = None
        self._cnf, self._controls, self._targets = self._make_revcirc_cnf()

    def _make_revcirc_cnf(self):
        cnf = CNF()
        width_iter = range(self._width)
        gc_iter = range(self._gate_count)
        input_iter = range(self._words)
        print(f"{self._width = } {self._gate_count = } {self._words = }")

        # i - qubit index, j - layer index, w - input word index
        controls = [[cnf.reserve_name(f"c_{i}_{j}") for i in width_iter] for j in gc_iter]
        targets = [[cnf.reserve_name(f"t_{i}_{j}") for i in width_iter] for j in gc_iter]
        print(targets)

        data_bits = [[[cnf.reserve_name(f"d_{i}_{j}_{w}") for i in width_iter]
                      for j in range(self._gate_count+1)] for w in input_iter]
        switch_bits = [[[cnf.reserve_name(f"s_{i}_{j}_{w}") for i in width_iter]
                        for j in gc_iter] for w in input_iter]
        add_bits = [[cnf.reserve_name(f"a_{j}_{w}") for j in gc_iter] for w in input_iter]
        or_bits = [[[cnf.reserve_name(f"o_{i}_{j}_{w}") for i in width_iter]
                    for j in gc_iter] for w in input_iter]

        # General circuit constraints
        # Single target per gate
        for target_layer in targets:
            cnf.exactly(target_layer, 1)

        # Target qubit cannot be a control qubit
        for i, j in product(width_iter, gc_iter):
            print(f"{i=} {j=}")
            cnf.nand(targets[j][i], controls[j][i])

        # Data flow constraints
        # Target qubit is the data bit
        for i, j, w in product(width_iter, gc_iter, input_iter):
            cnf.equals_or(or_bits[w][j][i], [data_bits[w][j][i], -controls[j][i]])

        # Add bit is the or of all or bits
        for j, w in product(gc_iter, input_iter):
            l_list = [or_bits[w][j][i] for i in width_iter]
            cnf.equals_and(add_bits[w][j], l_list)

        # Switch bit is the add bit and the target qubit
        for i, j, w in product(width_iter, gc_iter, input_iter):
            cnf.equals_and(switch_bits[w][j][i], [add_bits[w][j], targets[j][i]])

        # Data bit is the previous data bit xored with the switch bit
        for i, j, w in product(width_iter, range(self._gate_count - 1), input_iter):
            cnf.xor([data_bits[w][j+1][i], data_bits[w][j][i], switch_bits[w][j][i]])

        # Input/Output edge constraints
        for i, w in product(width_iter, input_iter):
            cnf.set_literal(data_bits[w][0][i], (w >> i & 1 == 1))

        for i, w in product(width_iter, input_iter):
            if self._output[w][i] in [0, 1]:
                a = data_bits[w][self._gate_count][i]
                b = (self._output[w][i] == 1)
                cnf.set_literal(a, b)

        return cnf, controls, targets

    def solve(self):
        width_iter = range(self._width)
        gc_iter = range(self._gate_count)
        self.solution = self._solver.solve(self._cnf)
        if not self.solution["sat"]:
            self.circuit = None
            return self.circuit
        circuit = Circuit(self._width)
        print(self.solution)
        for j in gc_iter:
            targets = [i for i in width_iter if self.solution[f"t_{i}_{j}"]]
            controls = [i for i in width_iter if self.solution[f"c_{i}_{j}"]]
            print(targets, controls)
            assert len(targets) == 1
            circuit.append((controls, targets[0]))
        self._circuit = circuit
        print(self._circuit.tt())
        return self._circuit
