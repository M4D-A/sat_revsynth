from truth_table.truth_table import TruthTable
from sat.solver import Solver
from synthesizer.synthesizer import Synthesizer
tt = TruthTable(2)
s = Solver("kissat")
sy = Synthesizer(tt, 4, s)
c = sy.solve()
print(c)
