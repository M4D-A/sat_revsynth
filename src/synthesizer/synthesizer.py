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


class Synthesiser:
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
        self.max_clauses_len = 3
        self.encoding = 1
        # self.solution = None
        # self.circuit = None

    def _make_revcirc_cnf(self):
        cnf = CNF()
        width_iter = range(self._width)
        gc_iter = range(self._gate_count)
        input_iter = range(self._words)

        # i - qubit index, j - layer index, w - input word index
        controls = [[cnf.reserve_name(f"c_{i}_{j}") for i in width_iter] for j in gc_iter]
        targets = [[cnf.reserve_name(f"t_{i}_{j}") for i in width_iter] for j in gc_iter]

        data_bits = [[[cnf.reserve_name(f"d_{i}_{j}_{w}") for i in width_iter]
                      for j in gc_iter] for w in input_iter]
        switch_bits = [[[cnf.reserve_name(f"s_{i}_{j}_{w}") for i in width_iter]
                        for j in gc_iter] for w in input_iter]
        add_bits = [[cnf.reserve_name(f"a_{j}_{d}") for j in gc_iter] for d in input_iter]
        or_bits = [[[cnf.reserve_name(f"o_{i}_{j}_{w}") for i in width_iter]
                    for j in gc_iter] for w in input_iter]

        # General circuit constraints
        # Single target per gate
        for target_layer in targets:
            cnf.exactly(target_layer, 1)

        # Target qubit cannot be a control qubit
        for i, j in product(width_iter, gc_iter):
            cnf.nand(targets[i][j], controls[i][j])

        # Data flow constraints
        # Target qubit is the data bit
        for i, j, w in product(width_iter, gc_iter, input_iter):
            cnf.equals_or(or_bits[i][j][w], [data_bits[i][j][w], -controls[i][j]])

        # Add bit is the or of all or bits
        for j, w in product(gc_iter, input_iter):
            l_list = [or_bits[i][j][w] for i in width_iter]
            cnf.equals_and(add_bits[j][w], l_list)

        # Switch bit is the add bit and the target qubit
        for i, j, w in product(width_iter, gc_iter, input_iter):
            cnf.equals_and(switch_bits[i][j][w], [add_bits[j][w], targets[i][j]])

        # Data bit is the previous data bit xored with the switch bit
        for i, j, w in product(width_iter, gc_iter, input_iter):
            cnf.xor([data_bits[i][j+1][w], data_bits[i][j][w], switch_bits[i][j][w]])

        # Input/Output edge constraints
        for i, w in product(width_iter, input_iter):
            cnf.set_literal(data_bits[i][0][w], (w >> i & 1 == 1))

        for i, w in product(width_iter, input_iter):
            if self._output[w][i] in [0, 1]:
                cnf.set_literal(data_bits[i][self._gate_count][w], (self._output[w][i] == 1))

        return cnf, controls, targets
