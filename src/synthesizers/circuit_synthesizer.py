from circuit.circuit import Circuit, Gate
from truth_table.truth_table import TruthTable
from sat.cnf import CNF, Literal
from sat.solver import Solver
from itertools import product
from functools import reduce


LiteralGrid = list[list[Literal]]


class CircuitSynthesizer:
    def __init__(self,
                 output: TruthTable,
                 gate_count: int,
                 solver: Solver,
                 # **kwargs
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
        self._circuit = None
        self._cnf, self._controls, self._targets = self._make_revcirc_cnf()

    def _make_revcirc_cnf(self) -> tuple[CNF, LiteralGrid, LiteralGrid]:
        cnf = CNF()
        line_iter = range(self._width)
        gate_iter = range(self._gate_count)
        gate_iter_ext = range(self._gate_count + 1)
        word_iter = range(self._words)

        controls = [[cnf.reserve_name(f"c_{lid}_{gid}") for lid in line_iter] for gid in gate_iter]
        targets = [[cnf.reserve_name(f"t_{lid}_{gid}") for lid in line_iter] for gid in gate_iter]
        or_bits = [[[cnf.reserve_name(f"o_{lid}_{gid}_{wid}") for lid in line_iter]
                    for gid in gate_iter] for wid in word_iter]
        data_bits = [[[cnf.reserve_name(f"d_{lid}_{gid}_{wid}") for lid in line_iter]
                      for gid in gate_iter_ext] for wid in word_iter]
        add_bits = [[cnf.reserve_name(f"a_{gid}_{wid}") for gid in gate_iter] for wid in word_iter]
        switch_bits = [[[cnf.reserve_name(f"s_{lid}_{gid}_{w}") for lid in line_iter]
                        for gid in gate_iter] for w in word_iter]

        # Single target per gate
        for target_layer in targets:
            cnf.exactly(target_layer, 1)

        # Target qubit cannot be a control qubit
        for lid, gid in product(line_iter, gate_iter):
            cnf.nand(targets[gid][lid], controls[gid][lid])

        # Target qubit is the data bit
        for lid, gid, wid in product(line_iter, gate_iter, word_iter):
            cnf.equals_or(or_bits[wid][gid][lid], [data_bits[wid][gid][lid], -controls[gid][lid]])

        # Add bit is the or of all or bits
        for gid, wid in product(gate_iter, word_iter):
            l_list = [or_bits[wid][gid][lid] for lid in line_iter]
            cnf.equals_and(add_bits[wid][gid], l_list)

        # Switch bit is the add bit and the target qubit
        for lid, gid, wid in product(line_iter, gate_iter, word_iter):
            cnf.equals_and(switch_bits[wid][gid][lid], [add_bits[wid][gid], targets[gid][lid]])

        # Data bit is the previous data bit xored with the switch bit
        for lid, gid, wid in product(line_iter, gate_iter, word_iter):
            cnf.xor([data_bits[wid][gid+1][lid], data_bits[wid]
                    [gid][lid], switch_bits[wid][gid][lid]])

        # Input/Output edge constraints
        for lid, wid in product(line_iter, word_iter):
            cnf.set_literal(data_bits[wid][0][lid], (wid >> lid & 1 == 1))

        for lid, wid in product(line_iter, word_iter):
            if self._output[wid][lid] in [0, 1]:
                a = data_bits[wid][self._gate_count][lid]
                b = (self._output[wid][lid] == 1)
                cnf.set_literal(a, b)

        return cnf, controls, targets

    def _gate_exclusion_list(self, layer: int, gate: Gate) -> list[int]:
        controls, target = gate
        assert layer < self._gate_count
        assert all([0 <= c and c < self._width] for c in controls)
        assert 0 <= target and target < self._width
        exclusion_list: list[int] = []
        for i in range(self._width):
            c_literal = self._controls[layer][i].value()
            c_literal = c_literal if i in controls else -c_literal
            t_literal = self._targets[layer][i].value()
            t_literal = t_literal if i == target else -t_literal
            exclusion_list += [c_literal, t_literal]
        return exclusion_list

    def exclude_subcircuit(self, circuit: Circuit) -> "CircuitSynthesizer":
        if circuit._exclusion_list is None:
            gates = circuit.gates()
            exclusion_list: list[int] = []
            for layer, gate in enumerate(gates):
                exclusion_list += self._gate_exclusion_list(layer, gate)
            circuit._exclusion_list = exclusion_list
        self._cnf.exclude_by_values(circuit._exclusion_list)
        return self

    def disable_empty_lines(self) -> "CircuitSynthesizer":
        line_iter = range(self._width)
        gate_iter = range(self._gate_count)
        for lid in line_iter:
            line_targets = [self._targets[gid][lid] for gid in gate_iter]
            line_controls = [self._controls[gid][lid] for gid in gate_iter]
            line_variables = line_targets + line_controls
            self._cnf.atleast(line_variables, 1)
        return self

    def disable_full_control_lines(self) -> "CircuitSynthesizer":
        line_iter = range(self._width)
        gate_iter = range(self._gate_count)
        for lid in line_iter:
            line_controls = [-self._controls[gid][lid] for gid in gate_iter]
            self._cnf.atleast(line_controls, 1)
        return self

    def set_global_controls_num(self, controls_num: int) -> "CircuitSynthesizer":
        assert 0 <= controls_num and controls_num <= (self._width - 1) * self._gate_count
        self._global_controls_num = controls_num
        all_controls = reduce(lambda x, y: x+y, self._controls)
        self._cnf.exactly(all_controls, controls_num)
        return self

    def solve(self) -> Circuit | None:
        if self._circuit is None:
            line_iter = range(self._width)
            gate_iter = range(self._gate_count)
            sat, literals = self._solver.solve(self._cnf)
            if not sat:
                self.circuit = None
                return self.circuit
            circuit = Circuit(self._width)
            for gid in gate_iter:
                targets = [lid for lid in line_iter if self._targets[gid][lid].value() in literals]
                controls = [lid for lid in line_iter if self._controls[gid][lid].value()
                            in literals]
                assert len(targets) == 1
                circuit.append((controls, targets[0]))
            self._circuit = circuit
        return self._circuit
