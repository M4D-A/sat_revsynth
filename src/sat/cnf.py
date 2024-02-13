from collections.abc import Iterable
from pysat.formula import CNF as CNF_core, IDPool
from pysat.card import CardEnc
from itertools import product
from timeit import default_timer as timer
import threading
import queue

VarName = str


class Literal:
    def __init__(self, name: VarName, id: int, value: bool | None = None):
        self.__name = name

        assert not id == 0, "ID cannot be equal to zero"
        if value is None:
            self.__value = id
        else:
            assert id > 0, "ID must be an absolute value if bool value stated"
            self.__value = id if value else -id

    def __bool__(self) -> bool:
        return self.__value > 0

    def __neg__(self):
        return Literal(self.__name, -self.__value)

    def __str__(self) -> str:
        return f"{self.__name}: {self.__bool__()} ({self.__value})"

    def value(self) -> int:
        return self.__value

    def name(self) -> str:
        return self.__name

    def __eq__(self, other) -> bool:
        return (self.name(), self.value()) == (other.name(), other.value())

    def __abs__(self):
        return Literal(self.__name, abs(self.__value))


class CNF():
    app_time = 0.0
    lcomp_time = 0.0
    ex_time = 0.0

    def __init__(self):
        self._cnf = CNF_core()
        self._v_pool = IDPool(start_from=1)
        self._max_clause_len = 3
        self._caridnality_enc = 1
        self._v_counter = 0

    def __str__(self) -> str:
        clauses = self.clauses()
        string = "clauses:\n" + \
            "\n".join([str(clause) for clause in clauses]) + "\n\n"
        string += "literals:\n" + \
            "\n".join([f"{name}: {value}" for name,
                      value in self._v_pool.obj2id.items()]) + "\n"
        return string

    def clauses(self) -> list[list]:
        return self._cnf.clauses

    def v_pool(self) -> IDPool:
        return self._v_pool

    def to_file(self, file_name: str) -> None:
        clauses = self._cnf.clauses
        cls_num = len(clauses)
        buffer_size = 1024*1024
        step = 2000
        if cls_num > 10000:
            def producer(out_q):
                header = f"p cnf {self._cnf.nv} {cls_num}\n"
                out_q.put(header)

                for i in range(0, cls_num, step):
                    clauses_slice = clauses[i: i + step]
                    string = ' 0\n'.join([' '.join([str(lit) for lit in cl])
                                          for cl in clauses_slice]) + ' 0\n'
                    out_q.put(string)
                out_q.put(None)

            def consumer(in_q, out_file):
                while True:
                    item = in_q.get()
                    if item is None:
                        break
                    out_file.write(item)

            q = queue.Queue()
            with open(file_name, 'w', buffering=buffer_size) as f:
                t1 = threading.Thread(target=producer, args=(q,))
                t2 = threading.Thread(target=consumer, args=(q, f))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
        else:
            header = f"p cnf {self._cnf.nv} {len(self._cnf.clauses)}\n"
            string = ' 0\n'.join([' '.join([str(lit) for lit in cl])
                                 for cl in self._cnf.clauses]) + ' 0\n'
            with open(file_name, "w", buffering=buffer_size) as fp:
                fp.write(header + string)

    def check_name(self, name: VarName) -> bool:
        return name in self._v_pool.obj2id.keys()

    def check_id(self, id: int) -> bool:
        return abs(id) in self._v_pool.obj2id.values()

    def verify_literals(self, literals: list[Literal]) -> bool:
        for lit in literals:
            name = lit.name()
            if not self.check_name(name):
                return False
            found = self.name_to_literal(name)
            if found is None or not (abs(lit) == abs(found)):
                return False
        return True

    def reserve_name(self, name: VarName, internal: bool = False) -> Literal:
        if internal:
            assert name[0].isupper(), \
                "Internal variable name cannot start with lowercase letter"
        else:
            assert name[0].islower(), \
                "Regular variable name cannot start with uppercase letter"
        assert name not in self._v_pool.obj2id, "Name already registered"
        id = self._v_pool.id(name)
        return Literal(name, id)

    def reserve_names(
        self,
        names: Iterable[str],
        internal: bool = False
    ) -> list[Literal]:
        return [self.reserve_name(name, internal) for name in names]

    def name_to_literal(self, name: VarName) -> Literal:
        assert name in self._v_pool.obj2id.keys(), "Name not found in the pool"
        id = self._v_pool.id(name)
        return Literal(name, id)

    def id_to_literal(self, id: int) -> Literal:
        abs_id = abs(id)
        pool = self._v_pool
        assert abs_id in pool.obj2id.values(), "ID not found in the pool"
        name = str(pool.obj(abs_id))
        return Literal(name, id)

    def set_literal(self, literal: Literal, value: bool | None = None):
        lval = literal.value()
        if value is not None:
            sign = 1 if value else -1
            lval = sign * abs(lval)
        self._cnf.append([lval])
        return self

    def set_literals(self, literals: list[Literal]):
        for lit in literals:
            self.set_literal(lit)
        return self

    def equals(self, literal_a: Literal, literal_b: Literal):
        lval_a = literal_a.value()
        lval_b = literal_b.value()
        self._cnf.append([-lval_a, lval_b])
        self._cnf.append([lval_a, -lval_b])
        return self

    def equals_and(self, literal_a: Literal, literals_b: list[Literal]):
        lval_a = literal_a.value()
        self._cnf.append([lval_a] + [-(b_elem.value())
                         for b_elem in literals_b])
        new_clauses = [[-lval_a, b_elem.value()] for b_elem in literals_b]
        self._cnf.clauses += new_clauses
        return self

    def equals_and_by_values(self, literal_a: int, literals_b: list[int]):
        header_clauses = [[literal_a] + [-b_elem for b_elem in literals_b]]
        new_clauses = header_clauses + [[-literal_a, b_elem] for b_elem in literals_b]
        self._cnf.clauses += new_clauses
        return self

    def equals_or(self, literal_a: Literal, literals_b: list[Literal]):
        lval_a = literal_a.value()
        self._cnf.append([-lval_a] + [b_elem.value()
                         for b_elem in literals_b])
        new_clauses = [[lval_a, -b_elem.value()] for b_elem in literals_b]
        self._cnf.clauses += new_clauses
        return self

    def xor(self, literals: list[Literal]):
        clause_len = self._max_clause_len
        if clause_len and clause_len <= 2:
            raise ValueError("split must be greater than 2 if set to True")
        if not clause_len or len(literals) <= clause_len:
            ones = [[1, -1] for _ in literals]
            ids = [a_elem.value() for a_elem in literals]
            for prod in product(*ones):
                if (sum(prod) - len(literals) + 2) % 4 == 0:
                    self._cnf.append(
                        [one * a_id for one, a_id in zip(prod, ids)])
        else:
            _ = [a_elem.value() for a_elem in literals]
            slice = literals[:clause_len - 1]
            aux_literal = self.reserve_name(f"A{self._v_counter}", True)
            self._v_counter += 1
            self.xor([aux_literal] + slice)
            self.xor([aux_literal] + literals[clause_len - 1:])
        return self

    def atleast(self, literals: list[Literal], lower_bound: int):
        ids = [lit.value() for lit in literals]
        clauses = CardEnc.atleast(
            ids,
            lower_bound,
            encoding=self._caridnality_enc,
            vpool=self._v_pool
        )
        self._cnf.extend(clauses)
        return self

    def atmost(self, literals: list[Literal], upper_bound: int):
        ids = [lit.value() for lit in literals]
        clauses = CardEnc.atmost(
            ids,
            upper_bound,
            encoding=self._caridnality_enc,
            vpool=self._v_pool
        )
        self._cnf.extend(clauses)
        return self

    def exactly(self, literals: list[Literal], upper_bound: int):
        ids = [lit.value() for lit in literals]
        clauses = CardEnc.equals(
            ids,
            upper_bound,
            encoding=self._caridnality_enc,
            vpool=self._v_pool
        )
        self._cnf.extend(clauses)
        return self

    def nand(self, literal_a: Literal, literal_b: Literal):
        lval_a = literal_a.value()
        lval_b = literal_b.value()
        self._cnf.append([-lval_a, -lval_b])
        return self

    def exclude(self, literals: list[Literal]):
        aux_literal = self.reserve_name(f"A{self._v_counter}", True)
        self._v_counter += 1
        self.equals_and(aux_literal, literals)
        self.set_literal(-aux_literal)
        return self

    def exclude_by_values(self, literals: list[int]):
        aux_literal = self.reserve_name(f"A{self._v_counter}", True)
        self._v_counter += 1
        self.equals_and_by_values(aux_literal.value(), literals)
        self.set_literal(-aux_literal)
        return self
