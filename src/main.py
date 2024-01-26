from sat import CNF
from sat import Solver

cnf = CNF()
a = cnf.reserve_name("a")
b = cnf.reserve_name("b")
cnf.equals(a, b)

s = Solver("kissat")
model = s.solve(cnf)
print(model)
