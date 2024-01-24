from pysat.formula import CNF as CNF_core, IDPool
from pysat.card import CardEnc
from itertools import product

VariableName = str
class Variable:
    def __init__(self, name: VariableName, id: int, value: bool|None = None):
        self.__name = name

        assert not id == 0, "ID cannot be equal to zero"
        if value is None:
            self.__id = id
        else:
            id = abs(id)
            self.__id = id if value else -id

    def __bool__(self):
        return self.__id > 0

    def __neg__(self):
        return Variable(self.__name, -self.__id)

    def __str__(self):
        return f"{self.__name}: {self.__bool__()} ({self.__id})"


class CNF():
    def __init__(self, max_clause_len: int|None = None, cardinality_encoding: int = 1):
        assert max_clause_len is None or max_clause_len >= 3, "max_clause_len must be greater than 2"
        self._cnf = CNF_core()
        self._v_pool = IDPool(start_from = 1)
        self._max_clause_len = max_clause_len
        self._caridnality_encoding = cardinality_encoding
        self._v_counter = 0
        
    def __str__(self) -> str:
        clauses = self.clauses()
        string = "\n".join([str(clause) for clause in clauses]) + "\n\n"
        string += "\n".join([f"{name}: {value}" for name, value in self._v_pool.obj2id.items()]) + "\n"
        return string

    def clauses(self) -> list[list]:
        return self._cnf.clauses

    def v_pool(self) -> IDPool:
        return self._v_pool

    def to_file(self, file_name: str) -> None:
        self._cnf.to_file(file_name) # [BOTTLENECK]

    def variable(self, id: int) -> Variable:
        return Variable(str(self._v_pool.obj(id)), id, True)

    def reserve_name(self, name: VariableName, internal: bool = False) -> Variable:
        if internal:
            assert name[0].isupper(), "Name cannot start with lowercase letter for internal variables"
        else:
            assert name[0].islower(), "Name cannot start with uppercase letter for regular variables"
        assert name not in self._v_pool.obj2id, "Name already registered"
        id = self._v_pool.id(name)
        return Variable(name, id)

    def find_variable(self, name: VariableName|int) -> Variable:
        if name is VariableName:
            assert name in self._v_pool.obj2id.keys(), "Name not found"
            id = self._v_pool.id(name)
        elif name is int:
            assert name in self._v_pool.obj2id.values(), "Id not found"
            id = name
            name = str(self._v_pool.obj(id))
        else:
            raise RuntimeError("Variables can be found only by their ids or names")
        return Variable(name, id)

    def set(self, var: Variable, value: bool = True):
        a_int = var.__id
        self._cnf.append([a_int if value else -a_int])

    def equals(self, var_a: Variable, var_b: Variable):
        a_int = self.get_id(var_a)
        b_int = self.get_id(var_b)
        self._cnf.append([-a_int, b_int])
        self._cnf.append([a_int, -b_int])
    
    def equals_and(self, a: Variable, b: list[Variable]):
        split = self._max_clause_len
        if split and split <= 2:
            raise ValueError("split must be greater than 2 if set to True")
        if not split or len(b) <= split-1:
            a_int = self.get_id(a)
            self._cnf.append([a_int] + [-self.get_id(b_elem) for b_elem in b])
            for b_elem in b:
                b_int = self.get_id(b_elem)
                self._cnf.append([-a_int, b_int])
        else:
            _ = [self.get_id(b_elem) for b_elem in b]
            b_cut = b[:split-1]
            and_cut = (True, f"A{self._v_counter}")
            self._v_counter += 1
            self.equals_and(and_cut, b_cut)
            self.equals_and(a, [and_cut] + b[split-1:])

    def equals_or(self, a: Variable, b: list[Variable]):
        split = self._max_clause_len
        if split and split <= 2:
            raise ValueError("split must be greater than 2 if set to True")
        if not split or len(b) <= split-1:
            a_int = self.get_id(a)
            self._cnf.append([-a_int] + [self.get_id(b_elem) for b_elem in b])
            for b_elem in b:
                b_int = self.get_id(b_elem)
                self._cnf.append([a_int, -b_int])
        else:
            _ = [self.get_id(b_elem) for b_elem in b]
            b_cut = b[:split-1]
            or_cut = (True, f"A{self._v_counter}")
            self._v_counter += 1
            self.equals_or(or_cut, b_cut)
            self.equals_or(a, [or_cut] + b[split-1:])

    def xor(self, a: list[Variable]):
        split = self._max_clause_len
        if split and split <= 2:
            raise ValueError("split must be greater than 2 if set to True")
        if not split or len(a) <= split:
            ones = [[1,-1] for _ in a]
            a_ids = [self.get_id(a_elem) for a_elem in a]
            for prod in product(*ones):
                if (sum(prod) - len(a) + 2) % 4 == 0:
                    self._cnf.append([one*a_id for one, a_id in zip(prod, a_ids)])
        else:
            _ = [self.get_id(a_elem) for a_elem in a]
            a_cut = a[:split-1]
            xor_cut = (True, f"A{self._v_counter}")
            self._v_counter += 1
            self.xor([xor_cut] + a_cut)
            self.xor([xor_cut] + a[split-1:])

    def atleast(self, a: list[Variable], k: int):
        a_id = [self.get_id(a_elem) for a_elem in a]
        clauses = CardEnc.atleast(a_id, k, encoding=self._caridnality_encoding, vpool = self._v_pool)
        self._cnf.extend(clauses)

    def atmost(self, a: list[Variable], k: int):
        a_id = [self.get_id(a_elem) for a_elem in a]
        clauses = CardEnc.atmost(a_id, k, encoding=self._caridnality_encoding, vpool = self._v_pool)
        self._cnf.extend(clauses)

    def exactly(self, a: list[Variable], k: int):
        a_id = [self.get_id(a_elem) for a_elem in a]
        clauses = CardEnc.equals(a_id, k, encoding=self._caridnality_encoding, vpool = self._v_pool)
        self._cnf.extend(clauses)
        
    def nand(self, a: Variable, b: Variable):
        a_id = self.get_id(a)
        b_id = self.get_id(b)
        self._cnf.append([-a_id, -b_id])

    def exclude(self, a: list[Variable]):
        exclude_var = (True, f"A{self._v_counter}")
        self._v_counter += 1
        self.equals_and(exclude_var, a)
        self.set(exclude_var, False)

