from sat.solver import Solver
from synthesizer.synthesizer import Synthesizer
from truth_table.truth_table import TruthTable
from circuit.circuit import Circuit
from multiprocessing import Pool
from itertools import repeat
from timeit import default_timer as timer
DimGroup = list[Circuit]


class PartialSynthesiser:
    def __init__(self, width: int, gate_count: int):
        self._width = width
        self._gate_count = gate_count
        self._synthesizer = Synthesizer(
            TruthTable(width),
            self._gate_count,
            solver=Solver("kissat")
        )
        self._synthesizer.disable_empty_lines()
        self._synthesizer.disable_full_control_lines()

    def synthesize(self) -> tuple[list[Circuit], float, float]:
        synth_start = timer()
        circuit = self._synthesizer.solve()
        synth_time = timer() - synth_start
        if (circuit):
            unroll_start = timer()
            equivalents = circuit.unroll()
            unroll_time = timer() - unroll_start
            return equivalents, synth_time, unroll_time
        else:
            return [], synth_time, 0.0

    def restrict_global_controls(self, controls_num: int):
        self._synthesizer.set_global_controls_num(controls_num)
        return self

    def exclude_subcircuit(self, circuit: Circuit):
        self._synthesizer.exclude_subcircuit(circuit)
        return self


class DimGroupSynthesizer:
    def __init__(self, width: int, gate_count: int):
        self._width = width
        self._gate_count = gate_count

    def synthesize(self, controls_num: int | None = None, initial: list[Circuit] = []) -> list[Circuit]:
        cnum = controls_num
        dim_group = [circ for circ in initial if circ.controls_num() == cnum or cnum is None]
        initial_size = len(dim_group)
        gst = 0.0
        gut = 0.0
        while True:
            ps = PartialSynthesiser(self._width, self._gate_count)
            if cnum is not None:
                ps.restrict_global_controls(cnum)
            for circuit in dim_group:
                ps.exclude_subcircuit(circuit)
            dim_partial_group, st, ut = ps.synthesize()
            gst += st
            gut += ut
            if (dim_partial_group):
                dim_group += dim_partial_group
            else:
                break
        print(f"- {cnum:2}: {gst:6.2f}s / {gut:6.2f}s -- {len(dim_group): 7} ({initial_size} initial) circuits")
        return dim_group

    def synthesize_mt(self, threads: int, initial: list[Circuit] = []):
        width = self._width
        gate_count = self._gate_count
        max_controls_num = (width - 1) * gate_count
        controls_num_range = range(max_controls_num + 1)

        with Pool(threads) as p:
            results = list(p.starmap(self.synthesize, zip(controls_num_range, repeat(initial))))

        dim_group = []
        for subgroup in results:
            dim_group += subgroup
        return dim_group
