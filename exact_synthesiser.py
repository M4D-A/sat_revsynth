
class exact_synthesiser:
    def __init__(
            self,
            output: list[list[int]],
            gc: int,
            max_controls: int | None = None,
            ancilla_num: int = 0,
            max_clauses_len: int = 3,
            encoding: int = 1,
            solver: solver = solver("cadical")):
        assert len(output) >= 2
        assert len(output) == pow(2, len(output[0]))
        assert all(len(word) == len(output[0]) for word in output)
        assert gc >= 0
        assert max_controls is None or max_controls >= 0
        assert ancilla_num >= 0
        assert max_clauses_len >= 3

        self.output = output
        self.gc = gc
        self.ancilla_num = ancilla_num
        self.max_clauses_len = max_clauses_len
        self.encoding = encoding
        self.solver = solver
        self.width = len(output[0])
        self.words = len(output)
        self.solution = None
        self.circuit = None
        self.cnf, self.controls, self.targets = self._make_revcirc_cnf()

    def solve(self) -> Circuit | None:
        if self.solution is None:
            self.solution = self.solver.solve(self.cnf)
            if not self.solution["sat"]:
                self.circuit = None
                return self.circuit
            circuit = Circuit(self.width)
            for t_layer, c_layer in zip(self.targets, self.controls):
                targets = [i for i, t in enumerate(t_layer) if self.solution[t[1]]]
                controls = [i for i, c in enumerate(c_layer) if self.solution[c[1]]]
                assert len(targets) == 1
                circuit.append((controls, targets[0]))
            self.circuit = circuit
        return self.circuit

    def exclude_subcircuit(self, qc: Circuit, shift: int = 0):
        gates = qc.gates
        exclusion_list = []
        for layer, gate in enumerate(gates):
            controls, target = gate
            targeted_layer = (layer + shift) % self.gc
            exclusion_list += self._gate_exclusion_list(targeted_layer, controls, target)
        self.cnf.exclude(exclusion_list)
        return self

    def set_max_gate_controls(self, max_controls_num: int):
        assert 0 <= max_controls_num and max_controls_num < self.width
        self.max_gate_controls_num = max_controls_num
        for control_layer in self.controls:
            self.cnf.atmost(control_layer, self.max_gate_controls_num)
        return self

    def set_global_controls_num(self, controls_num: int):
        assert 0 <= controls_num and controls_num <= (self.width - 1) * self.gc
        self.global_controls_num = controls_num
        all_controls = reduce(lambda x, y: x+y, self.controls)
        self.cnf.exactly(all_controls, self.global_controls_num)
        return self

    def _gate_exclusion_list(self, layer: int, controls: list[int], target: int) -> list[int]:
        assert layer < self.gc
        assert all([0 <= c and c < self.width] for c in controls)
        assert 0 <= target and target < self.width
        neg = vcnf.neg
        exclusion_list = []
        for i in range(self.width):
            c_literal = self.controls[layer][i] if i in controls else neg(self.controls[layer][i])
            t_literal = self.targets[layer][i] if i == target else neg(self.targets[layer][i])
            exclusion_list += [c_literal, t_literal]
        return exclusion_list
