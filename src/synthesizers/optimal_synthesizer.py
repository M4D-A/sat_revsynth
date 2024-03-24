from circuit.circuit import Circuit, Gate
from truth_table.truth_table import TruthTable
from sat.solver import Solver
from synthesizers.circuit_synthesizer import CircuitSynthesizer


class OptimalSynthesizer:
    def __init__(self, output: TruthTable, lower_gc: int, upper_gc: int, solver: Solver):
        assert len(output) >= 2
        assert len(output) == pow(2, len(output[0]))
        assert all(len(word) == len(output[0]) for word in output)
        assert upper_gc >= lower_gc

        self._output = output
        self._lower_gc = lower_gc
        self._upper_gc = upper_gc
        self._solver = solver
        self._width = len(output[0])
        self._words = len(output)
        self._circuit = None

    def solve(self) -> Circuit | None:
        if self._circuit is not None:
            return self._circuit
        for gc in range(self._lower_gc, self._upper_gc + 1):
            print(f"Trying k = {gc}")
            c_synth = CircuitSynthesizer(self._output, gc, self._solver)
            circuit = c_synth.solve()
            if circuit:
                self._circuit = circuit
                return circuit
        return None
