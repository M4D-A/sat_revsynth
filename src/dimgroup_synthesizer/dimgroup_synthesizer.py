from sat.solver import Solver
from synthesizer.synthesizer import Synthesizer
from truth_table.truth_table import TruthTable
from circuit.circuit import Circuit

DimGroup = list[Circuit]


class PartialSynthesiser:
    def __init__(self, width: int, gate_count: int):
        self._width = width
        self._gate_count = gate_count
        self._synthesizer = Synthesizer(
            TruthTable(width),
            self._gate_count,
            solver=Solver("kissat")
        ).disable_empty_lines()

    def synthesise(self) -> list[Circuit]:
        circuit = self._synthesizer.solve()
        if (circuit):
            equivalents = circuit.unroll()
            return equivalents
        else:
            return []

    def exclude_subcircuit(self, circuit: Circuit):
        self._synthesizer.exclude_subcircuit(circuit)
        return self


class DimGroupSynthesiser:
    def __init__(self, width: int, gate_count: int):
        self._width = width
        self._gate_count = gate_count

    def synthesise(self, initial: list[Circuit] | None = None) -> list[Circuit]:
        dim_group = initial if initial is not None else []
        while True:
            ps = PartialSynthesiser(self._width, self._gate_count)
            for circuit in dim_group:
                ps.exclude_subcircuit(circuit)
            dim_partial_group = ps.synthesise()
            if (dim_partial_group):
                dim_group += dim_partial_group
            else:
                break
        unique = Circuit.filter_duplicates(dim_group)
        return unique
