import pytest
from random import randint, choice, sample
from itertools import product
from functools import reduce
from copy import deepcopy
from .cnf import CNF
from .solver import Solver

solver_names = Solver.available_solvers
solvers = [Solver(solver_name) for solver_name in solver_names]
max_variables = 16
short_max_variables = 6
epochs = range(1024)

@pytest.fixture
def triplet_cnf():
    cnf = CNF()
    literals = cnf.reserve_names(['a', 'b', 'c'])
    return (cnf, literals)

@pytest.fixture
def long_cnf():
    cnf = CNF()
    primary_literal = cnf.reserve_name("p")
    literals_num = randint(4, max_variables)
    literals = cnf.reserve_names(f"l{i}" for i in range(literals_num))
    return (cnf, primary_literal, literals)

def test_equals_true(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals(a, b).set_literal(a)
        model = solver.solve(cnf)
        assert model['sat']
        assert model[a.name()]
        assert model[b.name()]
        assert c.name() in model

def test_equals_false(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals(a, b).set_literal(-b)
        model = solver.solve(cnf)
        assert model['sat']
        assert not model[a.name()]
        assert not model[b.name()]
        assert c.name() in model

def test_equals_unsat(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, _) = triplet_cnf
        cnf.equals(a, b).set_literals([a, -b])
        model = solver.solve(cnf)
        assert not model['sat']

def test_and_true(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals_and(a, [b, c]).set_literal(a)
        model = solver.solve(cnf)
        assert model['sat']
        assert model[a.name()]
        assert model[b.name()]
        assert model[c.name()]

def test_and_false(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals_and(a, [b, c]).set_literal(-a)
        model = solver.solve(cnf)
        assert model['sat']
        assert not model[a.name()]
        assert not model[b.name()] or not model[c.name()]

def test_and_unsat(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals_and(a, [b, c]).set_literals([a, -b])
        model = solver.solve(cnf)
        assert not model['sat']

def test_and_true_long(long_cnf):
    for solver, _ in product(solvers, epochs):
        cnf, primary, literals = long_cnf
        cnf.equals_and(primary, literals).set_literal(primary)
        model = solver.solve(cnf)
        assert model['sat']
        assert model[primary.name()]
        assert all(model[lit.name()] for lit in literals)

def test_and_false_long(long_cnf):
    for solver, _ in product(solvers, epochs):
        cnf, primary, literals = long_cnf
        cnf.equals_and(primary, literals).set_literal(-primary)
        model = solver.solve(cnf)
        assert model['sat']
        assert not model[primary.name()]
        assert any(not model[lit.name()] for lit in literals)

def test_and_unsat_long(long_cnf):
    for solver, _ in product(solvers, epochs):
        cnf, primary, literals = long_cnf
        cnf.equals_and(primary, literals).set_literals([primary, -literals[0]])
        model = solver.solve(cnf)
        assert not model['sat']

def test_or_true(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals_or(a, [b, c]).set_literal(a)
        model = solver.solve(cnf)
        assert model['sat']
        assert model[a.name()]
        assert model[b.name()] or model[c.name()]

def test_or_false(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals_or(a, [b, c]).set_literal(-a)
        model = solver.solve(cnf)
        assert model['sat']
        assert not model[a.name()]
        assert not model[b.name()]
        assert not model[c.name()]

def test_or_unsat(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.equals_or(a, [b, c]).set_literals([-a, b])
        model = solver.solve(cnf)
        assert not model['sat']

def test_or_true_long(long_cnf):
    for solver, _ in product(solvers, epochs):
        cnf, primary, literals = long_cnf
        cnf.equals_or(primary, literals).set_literal(primary)
        model = solver.solve(cnf)
        assert model['sat']
        assert model[primary.name()]
        assert any(model[lit.name()] for lit in literals)

def test_or_false_long(long_cnf):
    for solver, _ in product(solvers, epochs):
        cnf, primary, literals = long_cnf
        cnf.equals_or(primary, literals).set_literal(-primary)
        model = solver.solve(cnf)
        assert model['sat']
        assert not model[primary.name()]
        assert all(not model[lit.name()] for lit in literals)

def test_or_unsat_long(long_cnf):
    for solver, _ in product(solvers, epochs):
        cnf, primary, literals = long_cnf
        cnf.equals_or(primary, literals).set_literals([-primary, literals[0]])
        model = solver.solve(cnf)
        assert not model['sat']

def test_xor_true(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.xor([a, b, c]).set_literal(a)
        model = solver.solve(cnf)
        assert model['sat']
        assert model[a.name()]
        assert model[b.name()] ^ model[c.name()]

def test_xor_false(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.xor([a, b, c]).set_literal(-a)
        model = solver.solve(cnf)
        assert model['sat']
        assert not model[a.name()]
        assert not (model[b.name()] ^ model[c.name()])

def test_xor_unsat(triplet_cnf):
    for solver in solvers:
        cnf, (a, b, c) = triplet_cnf
        cnf.xor([a, b, c]).set_literals([a, b, c])
        model = solver.solve(cnf)
        assert not model['sat']

def test_xor_true_long(long_cnf):
    for solver, _ in product(solvers[:1], epochs):
        cnf = CNF()
        cnf, primary, literals = deepcopy(long_cnf)
        xor_literals = literals + [primary]
        cnf.xor(xor_literals)
        literals_to_set = sample(xor_literals, randint(0, len(xor_literals)-1))
        set_literals = [var if randint(0,1) else -var for var in literals_to_set]
        cnf.set_literals(set_literals)
        model = solver.solve(cnf)
        for lit in literals_to_set:
            name = lit.name()
            if lit in set_literals:
                assert (model[name])
            if -lit in set_literals:
                assert not(model[name])
        value = reduce(lambda x,y : x^y, map(lambda var: model[var.name()], xor_literals))
        assert not(value)
#
# def test_atleast(self):
#     for solver, _ in product(self.solvers, self.epochs):
#         cnf = CNF()
#         literals_num = randint(3, self.max_variables)
#         literals = [cnf.reserve_name(f'b{i}') for i in range(literals_num)]
#
#         set_vars_num = randint(0, literals_num - 1)
#         literals_to_set = sample(literals, set_vars_num)
#         set_literals = [var if randint(0,1) else -var for var in literals_to_set]
#         set_false_num = sum([1 for var in set_literals if -var]) 
#
#         max_lower_bound = literals_num - set_false_num
#         lower_bound = randint(1, max_lower_bound)
#         cnf.atleast(literals, lower_bound)
#         cnf.set_literals(set_literals)
#         model = solver.solve(cnf)
#         self.assertTrue(model['sat'])
#         self.assertTrue(sum([model[lit.name()] for lit in literals]) >= lower_bound)
#
# def test_atmost(self):
#     for solver, _ in product(self.solvers, self.epochs):
#         cnf = CNF()
#         literals_num = randint(3, self.max_variables)
#         literals = [cnf.reserve_name(f'b{i}') for i in range(literals_num)]
#         set_vars_num = randint(0, literals_num - 1)
#         literals_to_set = sample(literals, set_vars_num)
#         set_literals = [lit if randint(0,1) else -lit for lit in literals_to_set]
#         set_true_num = sum([1 for lit in set_literals if lit]) 
#         min_upper_bound = set_true_num
#         upper_bound = randint(min_upper_bound, literals_num - 1)
#         cnf.atmost(literals, upper_bound)
#         cnf.set_literals(set_literals)
#         model = solver.solve(cnf)
#         self.assertTrue(model['sat'])
#         self.assertTrue(sum([model[lit.name()] for lit in literals]) <= upper_bound)
#
# if __name__ == '__main__':
# unittest.main()
