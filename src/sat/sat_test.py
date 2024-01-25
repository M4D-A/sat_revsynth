import unittest
from cnf import CNF
from solver import Solver
from random import randint, choice, sample
from itertools import product
from functools import reduce
from copy import deepcopy

class sat_test(unittest.TestCase):
    solver_names = Solver.available_solvers
    solvers = [Solver(solver_name) for solver_name in solver_names]
    max_variables = 32
    short_max_variables = 6
    epochs = range(128)

    def test_equals_true(self):
        for solver in self.solvers:
            cnf = CNF()
            a = cnf.reserve_name('a')
            b = cnf.reserve_name('b')
            cnf.equals(a,b)

            cnf_1 = deepcopy(cnf).set_literal(a)
            model = solver.solve(cnf_1)
            self.assertTrue(model["sat"], model)
            self.assertTrue(model[a.name()], model)
            self.assertTrue(model[b.name()], model)

            cnf_2 = deepcopy(cnf).set_literal(-a)
            model = solver.solve(cnf_2)
            self.assertTrue(model["sat"])
            self.assertFalse(model[a.name()])
            self.assertFalse(model[b.name()])

            cnf_3 = deepcopy(cnf).set_literals([-a, b])
            model = solver.solve(cnf_3)
            self.assertFalse(model["sat"])

    def test_short_and(self):
        for solver in self.solvers:
            cnf = CNF()
            a = cnf.reserve_name('a')
            b = cnf.reserve_name('b')
            c = cnf.reserve_name('c')
            cnf.equals_and(a, [b, c])

            cnf_1 = deepcopy(cnf).set_literal(a)
            model = solver.solve(cnf_1)
            self.assertTrue(model["sat"])
            self.assertTrue(model[a.name()])
            self.assertTrue(model[b.name()])
            self.assertTrue(model[c.name()])

            cnf_2 = deepcopy(cnf).set_literal(-a)
            model = solver.solve(cnf_2)
            self.assertTrue(model["sat"])
            self.assertFalse(model[a.name()])
            self.assertTrue(not model[b.name()] or not model[c.name()])
            
            cnf_3 = deepcopy(cnf).set_literals([a, -b])
            model = solver.solve(cnf_3)
            self.assertFalse(model['sat'])

    def test_long_and(self):
        for solver, _ in product(self.solvers, self.epochs):
            cut = randint(3, self.max_variables)
            cnf = CNF(max_clause_len=cut)
            and_literals_num = randint(3, self.max_variables)
            equal_literal = cnf.reserve_name("e")
            and_literals = [cnf.reserve_name(f"b{i}") for i in range(and_literals_num)]
            cnf.equals_and(equal_literal, and_literals)
            self.assertTrue(all([len(clause) <= cut for clause in cnf.clauses()]))
            
            cnf_1 = deepcopy(cnf).set_literal(equal_literal)
            model = solver.solve(cnf_1)
            self.assertTrue(model["sat"])
            self.assertTrue(model[equal_literal.name()])
            self.assertTrue(all([model[lit.name()] for lit in and_literals]))

            cnf_2 = deepcopy(cnf).set_literal(-equal_literal)
            model = solver.solve(cnf_2)
            self.assertTrue(model["sat"])
            self.assertFalse(model[equal_literal.name()])
            self.assertTrue(any([not model[lit.name()] for lit in and_literals]))

            cnf_3 = deepcopy(cnf).set_literals([equal_literal, -and_literals[0]])
            model = solver.solve(cnf_3)
            self.assertFalse(model["sat"])

    def test_short_or(self):
        for solver in self.solvers[:1]:
            cnf = CNF()
            a = cnf.reserve_name('a')
            b = cnf.reserve_name('b')
            c = cnf.reserve_name('c')
            cnf.equals_or(a, [b, c])

            cnf_1 = deepcopy(cnf).set_literal(a)
            model = solver.solve(cnf_1)
            self.assertTrue(model["sat"])
            self.assertTrue(model[a.name()])
            self.assertTrue(model[b.name()] or model[c.name()])

            cnf_2 = deepcopy(cnf).set_literal(-a)
            model = solver.solve(cnf_2)
            self.assertTrue(model["sat"])
            self.assertTrue(not model[a.name()])
            self.assertTrue(not model[b.name()])
            self.assertTrue(not model[c.name()])

            cnf_3 = deepcopy(cnf).set_literals([-a, b])
            model = solver.solve(cnf_3)
            self.assertFalse(model['sat'])

    def test_long_or(self):
        for solver, _ in product(self.solvers, self.epochs):
            cut = randint(3, self.max_variables)
            cnf = CNF(max_clause_len=cut)
            or_literals_num = randint(3, self.max_variables)
            equal_literal = cnf.reserve_name("e")
            or_literals = [cnf.reserve_name(f"b{i}") for i in range(or_literals_num)]
            cnf.equals_or(equal_literal, or_literals)
            self.assertTrue(all([len(clause) <= cut for clause in cnf.clauses()]))
            
            cnf_1 = deepcopy(cnf).set_literal(equal_literal)
            model = solver.solve(cnf_1)
            self.assertTrue(model["sat"])
            self.assertTrue(model[equal_literal.name()])
            self.assertTrue(any([model[lit.name()] for lit in or_literals]))

            cnf_2 = deepcopy(cnf).set_literal(-equal_literal)
            model = solver.solve(cnf_2)
            self.assertTrue(model["sat"])
            self.assertFalse(model[equal_literal.name()])
            self.assertTrue(all([not model[lit.name()] for lit in or_literals]))

            cnf_3 = deepcopy(cnf).set_literals([-equal_literal, or_literals[0]])
            model = solver.solve(cnf_3)
            self.assertFalse(model["sat"])

    def test_short_xor(self):
        for solver in self.solvers: 
            cnf = CNF()
            a = cnf.reserve_name('a')
            b = cnf.reserve_name('b')
            c = cnf.reserve_name('c')
            cnf.xor([a, b, c])

            cnf_1 = deepcopy(cnf).set_literal(a)
            model = solver.solve(cnf_1)
            self.assertTrue(model["sat"])
            self.assertTrue(model[a.name()])
            self.assertTrue(model[b.name()] ^ model[c.name()])

            cnf_1 = deepcopy(cnf).set_literal(-a)
            model = solver.solve(cnf_1)
            self.assertTrue(model["sat"])
            self.assertFalse(model[a.name()])
            self.assertFalse(model[b.name()] ^ model[c.name()])

            cnf_1 = deepcopy(cnf).set_literals([a, b, c])
            model = solver.solve(cnf_1)
            self.assertFalse(model["sat"])

    def test_long_xor(self):
        for solver, _ in product(self.solvers, self.epochs):
            cnf = CNF(max_clause_len=3)
            xor_literals_num = randint(3, self.max_variables)
            xor_literals = [cnf.reserve_name(f"b{i}") for i in range(xor_literals_num)]
            cnf.xor(xor_literals)
            literals_to_set = sample(xor_literals, randint(0, len(xor_literals)-1))
            set_literals = [var if randint(0,1) else -var for var in literals_to_set]
            cnf.set_literals(set_literals)
            model = solver.solve(cnf)
            for lit in literals_to_set:
                name = lit.name()
                if lit in set_literals:
                    self.assertTrue(model[name])
                if -lit in set_literals:
                    self.assertFalse(model[name])
            value = reduce(lambda x,y : x^y, map(lambda var: model[var.name()], xor_literals))
            self.assertFalse(value)

    def test_atleast(self):
        for solver, _ in product(self.solvers, self.epochs):
            cnf = CNF()
            literals_num = randint(3, self.max_variables)
            literals = [cnf.reserve_name(f"b{i}") for i in range(literals_num)]

            set_vars_num = randint(0, literals_num - 1)
            literals_to_set = sample(literals, set_vars_num)
            set_literals = [var if randint(0,1) else -var for var in literals_to_set]
            set_false_num = sum([1 for var in set_literals if -var]) 

            max_lower_bound = literals_num - set_false_num
            lower_bound = randint(1, max_lower_bound)
            cnf.atleast(literals, lower_bound)
            cnf.set_literals(set_literals)
            model = solver.solve(cnf)
            self.assertTrue(model["sat"])
            self.assertTrue(sum([model[lit.name()] for lit in literals]) >= lower_bound)

    def test_atmost(self):
        for solver, _ in product(self.solvers, self.epochs):
            cnf = CNF()
            literals_num = randint(3, self.max_variables)
            literals = [cnf.reserve_name(f"b{i}") for i in range(literals_num)]
            set_vars_num = randint(0, literals_num - 1)
            literals_to_set = sample(literals, set_vars_num)
            set_literals = [lit if randint(0,1) else -lit for lit in literals_to_set]
            set_true_num = sum([1 for lit in set_literals if lit]) 
            min_upper_bound = set_true_num
            upper_bound = randint(min_upper_bound, literals_num - 1)
            cnf.atmost(literals, upper_bound)
            cnf.set_literals(set_literals)
            model = solver.solve(cnf)
            self.assertTrue(model["sat"])
            self.assertTrue(sum([model[lit.name()] for lit in literals]) <= upper_bound)

if __name__ == '__main__':
    unittest.main()
