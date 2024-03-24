from sat.solver import Solver
from synthesizers.circuit_synthesizer import CircuitSynthesizer
from truth_table.truth_table import TruthTable
from circuit.circuit import Circuit
from circuit.dim_group import DimGroup
from multiprocessing import Pool


class PartialSynthesizer:
    def __init__(self, width: int, gate_count: int):
        self._width = width
        self._gate_count = gate_count
        self._synthesizer = CircuitSynthesizer(
            TruthTable(width),
            self._gate_count,
            solver=Solver("kissat")
        )
        self._synthesizer.disable_empty_lines()
        self._synthesizer.disable_full_control_lines()

    def synthesize(self) -> DimGroup:
        circuit = self._synthesizer.solve()
        dg = DimGroup(self._width, self._gate_count)
        if (bool(circuit)):
            dg.extend(circuit.unroll())
        return dg

    def restrict_global_controls(self, controls_num: int) -> "PartialSynthesizer":
        self._synthesizer.set_global_controls_num(controls_num)
        return self

    def exclude_subcircuit(self, circuit: Circuit) -> "PartialSynthesizer":
        self._synthesizer.exclude_solution(circuit)
        return self


class DimGroupSynthesizer:
    def __init__(self, width: int, gate_count: int):
        self._width = width
        self._gate_count = gate_count

    def synthesize(self, controls_num: int | None = None) -> DimGroup:
        cnum = controls_num
        dg = DimGroup(self._width, self._gate_count)
        while True:
            ps = PartialSynthesizer(self._width, self._gate_count)
            if cnum is not None:
                ps.restrict_global_controls(cnum)
            for circuit in dg:
                ps.exclude_subcircuit(circuit)
            partial_dg = ps.synthesize()
            if (bool(partial_dg)):
                dg.join(partial_dg)
            else:
                break
        return dg

    def synthesize_mt(self, threads: int) -> DimGroup:
        width = self._width
        gate_count = self._gate_count
        max_controls_num = (width - 1) * gate_count
        controls_num_range = range(max_controls_num + 1)

        with Pool(threads) as pool:
            results = list(pool.map(self.synthesize, controls_num_range))

        dg = DimGroup(self._width, self._gate_count)
        for subgroup in results:
            dg.join(subgroup)
        return dg
