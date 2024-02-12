from truth_table.truth_table import TruthTable
from sat.solver import Solver
from synthesizer.synthesizer import Synthesizer

tt = TruthTable(3)
s = Solver("kissat")

circuits = []
while True:
    sy = Synthesizer(tt, 4, s).disable_empty_lines()
    # sy = Synthesizer(tt, 4, s)
    for c in circuits:
        sy.exclude_subcircuit(c)
    c = sy.solve()
    if c is not None:
        circuits += c.unroll()
    else:
        break
print(len(circuits))
