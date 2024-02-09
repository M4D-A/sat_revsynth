from sat.cnf import CNF
from sat.solver import Solver
from truth_table.truth_table import TruthTable
tt = TruthTable(3)
print(tt)
cnf = CNF()
a = cnf.reserve_name("a")
b = cnf.reserve_name("b")
cnf.equals(a, b)

s = Solver("kissat")
model = s.solve(cnf)
print(model)
