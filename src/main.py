from truth_table.truth_table import TruthTable
from circuit.circuit import Circuit
from sat.cnf import CNF
from sat.solver import Solver
from synthesizer.synthesizer import Synthesizer
tt = TruthTable(3)
c = Circuit(3)
cnf = CNF()
s = Solver("kissat")
sy = Synthesizer(tt, 3, s)
c = sy.solve()
print(c)
