from inplace import inplace
from truth_table.truth_table import TruthTable
from cnf import CNF
t = TruthTable(2, [2, 1, 3, 0])
print(t)
cnf = CNF()
cnf.reserve_name("abc")
print(cnf)

# from sat.solver import Solver
# from sat.cnf import CNF
# from circuit.circuit import Circuit
# from synthesizer.synthesizer import Synthesiser
#
# t = TruthTable(2, [2, 1, 3, 0])
# s = Solver("kissat")
# synth = Synthesiser(t, 3, s)
# c = synth.solve()
# print(t)
# print(c)
