from pysat.formula import CNF as CNF_core, IDPool
from pysat.card import CardEnc
from itertools import product

VariableName = str
class Literal:
    def __init__(self, name: VariableName, literal_id: int, value: bool|None = None):
        self.__name = name

        assert not literal_id == 0, "ID cannot be equal to zero"
        if value is None:
            self.__value = literal_id
        else:
            assert literal_id > 0, "ID must be an absolute value if boolean value stated"
            self.__value = literal_id if value else -literal_id

    def __bool__(self) -> bool:
        return self.__value > 0

    def __neg__(self):
        return Literal(self.__name, -self.__value)

    def __str__(self) -> str:
        return f"{self.__name}: {self.__bool__()} ({self.__value})"

    def value(self) -> int:
        return abs(self.__value)
    
    def name(self) -> str:
        return self.__name

    def __eq__(self, other) -> bool:
        return (self.name(), self.value()) == (other.name(), other.value())


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

    def check_name(self, name: VariableName) -> bool:
        return name in self._v_pool.obj2id.keys()

    def verify_literals(self, literals: list[Literal]) -> bool:
        for lit in literals:
            name = lit.name()
            if not self.check_name(name):
                return False
            found = self.name_to_variable(name)
            if found is None or not (lit == found):
                return False
        return True

    def reserve_name(self, name: VariableName, internal: bool = False) -> Literal:
        if internal:
            assert name[0].isupper(), "Name cannot start with lowercase letter for internal variables"
        else:
            assert name[0].islower(), "Name cannot start with uppercase letter for regular variables"
        assert name not in self._v_pool.obj2id, "Name already registered"
        id = self._v_pool.id(name)
        return Literal(name, id)

    def name_to_variable(self, name: VariableName) -> Literal:
        assert name in self._v_pool.obj2id.keys(), "Name not found in the pool"
        id = self._v_pool.id(name)
        return Literal(name, id)

    def id_to_variable(self, id: int) -> Literal:
        assert id in self._v_pool.obj2id.values(), "ID not found in the pool"
        name = str(self._v_pool.obj(id))
        return Literal(name, id)

    def set_literal(self, literal: Literal) -> None:
        assert self.verify_literals([literal])
        lval_a = literal.value()
        self._cnf.append([lval_a])

    def equals(self, literal_a: Literal, literal_b: Literal) -> None:
        assert self.verify_literals([literal_a, literal_b])
        lval_a = literal_a.value()
        lval_b = literal_b.value()
        self._cnf.append([-lval_a, lval_b])
        self._cnf.append([lval_a, -lval_b])
    
    def equals_and(self, literal_a: Literal, literals_b: list[Literal]):
        assert self.verify_literals([literal_a] + literals_b)
        clause_len = self._max_clause_len
        if clause_len and clause_len <= 2:
            raise ValueError("clause_len must be greater than 2 if set to True")
        if not clause_len or len(literals_b) <= clause_len - 1:
            lval_a = literal_a.value()
            self._cnf.append([lval_a] + [-b_elem.value() for b_elem in literals_b])
            for b_elem in literals_b:
                lval_b = b_elem.value()
                self._cnf.append([-lval_a, lval_b])
        else:
            _ = [b_elem.value() for b_elem in literals_b]
            slice = literals_b[:clause_len-1]
            aux_literal = self.reserve_name(f"A{self._v_counter}")
            self._v_counter += 1
            self.equals_and(aux_literal, slice)
            self.equals_and(literal_a, [aux_literal] + literals_b[clause_len-1:])

    def equals_or(self, literal_a: Literal, literals_b: list[Literal]):
        assert self.verify_literals([literal_a] + literals_b)
        clause_len = self._max_clause_len
        if clause_len and clause_len <= 2:
            raise ValueError("clause_len must be greater than 2 if set to True")
        if not clause_len or len(literals_b) <= clause_len - 1:
            lval_a = literal_a.value()
            self._cnf.append([-lval_a] + [b_elem.value() for b_elem in literals_b])
            for b_elem in literals_b:
                lval_b = b_elem.value()
                self._cnf.append([lval_a, -lval_b])
        else:
            _ = [b_elem.value() for b_elem in literals_b]
            slice = literals_b[:clause_len-1]
            aux_literal = self.reserve_name(f"A{self._v_counter}")
            self._v_counter += 1
            self.equals_or(aux_literal, slice)
            self.equals_or(literal_a, [aux_literal] + literals_b[clause_len-1:])

    def xor(self, literals: list[Literal]):
        assert self.verify_literals(literals)
        clause_len = self._max_clause_len
        if clause_len and clause_len <= 2:
            raise ValueError("split must be greater than 2 if set to True")
        if not clause_len or len(literals) <= clause_len:
            ones = [[1,-1] for _ in literals]
            ids = [a_elem.value() for a_elem in literals]
            for prod in product(*ones):
                if (sum(prod) - len(literals) + 2) % 4 == 0:
                    self._cnf.append([one*a_id for one, a_id in zip(prod, ids)])
        else:
            _ = [a_elem.value() for a_elem in literals]
            slice = literals[:clause_len-1]
            aux_literal = self.reserve_name(f"A{self._v_counter}")
            self._v_counter += 1
            self.xor([aux_literal] + slice)
            self.xor([aux_literal] + literals[clause_len-1:])

    def atleast(self, literals: list[Literal], lower_bound: int):
        assert self.verify_literals(literals)
        ids = [lit.value() for lit in literals]
        clauses = CardEnc.atleast(ids, lower_bound, encoding=self._caridnality_encoding, vpool = self._v_pool)
        self._cnf.extend(clauses)

    def atmost(self, literals: list[Literal], upper_bound: int):
        assert self.verify_literals(literals)
        ids = [lit.value() for lit in literals]
        clauses = CardEnc.atleast(ids, upper_bound, encoding=self._caridnality_encoding, vpool = self._v_pool)
        self._cnf.extend(clauses)

    def exactly(self, literals: list[Literal], upper_bound: int):
        assert self.verify_literals(literals)
        ids = [lit.value() for lit in literals]
        clauses = CardEnc.equals(ids, upper_bound, encoding=self._caridnality_encoding, vpool = self._v_pool)
        self._cnf.extend(clauses)
        
    def nand(self, literal_a: Literal, literal_b: Literal) -> None:
        assert self.verify_literals([literal_a, literal_b])
        lval_a = literal_a.value()
        lval_b = literal_b.value()
        self._cnf.append([-lval_a, -lval_b])

    def exclude(self, literals: list[Literal]):
        aux_literal = self.reserve_name(f"A{self._v_counter}")
        self._v_counter += 1
        self.equals_and(aux_literal, literals)
        self.set_literal(-aux_literal)

