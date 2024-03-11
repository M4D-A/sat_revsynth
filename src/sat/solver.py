from pysat.solvers import Cadical153, Lingeling, Glucose4
from subprocess import Popen, PIPE
from sat.cnf import CNF, Solution

import threading
import queue


class Solver:
    external_solvers = {
        "kissat": ["-q"],
        # "cms":["--verb", "0"],
        # "parkissat": ["-v=1", "-c=8", "-max-memory=8"]
    }

    builtin_solvers = {
        "cadical": Cadical153,
        "lingeling": Lingeling,
        "glucose4": Glucose4
    }

    available_solvers = list(external_solvers.keys()) + \
        list(builtin_solvers.keys())

    def __init__(self, name: str, args=None):
        if name not in Solver.available_solvers:
            raise ValueError(f"Solver {name} not supported")
        self.__name = name
        self.__args = args

    def solve(self, cnf: CNF) -> Solution:
        if self.__name in self.builtin_solvers:
            solution = self._solve_builtin(cnf)
        elif self.__name in self.external_solvers:
            solution = self._solve_external(cnf)
        else:
            raise ValueError(f"Solver {self.__name} not supported")
        return solution

    def _solve_builtin(self, cnf: CNF) -> Solution:
        builtin_solver_class = self.builtin_solvers[self.__name]
        clauses = cnf.clauses()
        builtin_solver = builtin_solver_class(bootstrap_with=clauses)
        if builtin_solver.solve():
            ids = builtin_solver.get_model()
            return (True, ids)
        else:
            return (False, [])

    def _solve_external(self, cnf: CNF) -> Solution:
        args = self.external_solvers[self.__name]
        if self.__args is not None:
            args += self.__args
        p = Popen([self.__name, *args], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        clauses = cnf._cnf.clauses
        cls_num = len(clauses)
        step = 20000

        def producer(out_q):
            header = f"p cnf {cnf._cnf.nv} {cls_num}\n"
            out_q.put(header)
            for i in range(0, cls_num, step):
                clauses_slice = clauses[i: i + step]
                string = ' 0\n'.join([' '.join([str(lit) for lit in cl])
                                      for cl in clauses_slice]) + ' 0\n'
                out_q.put(string)
            out_q.put(None)

        def consumer(in_q, p):
            while True:
                item = in_q.get()
                if item is None:
                    break
                p.stdin.write(item.encode())
            p.stdin.close()

        q = queue.Queue()
        t1 = threading.Thread(target=producer, args=(q,))
        t2 = threading.Thread(target=consumer, args=(q, p))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert p.stdout is not None
        out = p.stdout.read()

        string = out.decode('utf-8')
        return self._parse_solution(string)

    @staticmethod
    def _parse_solution(string: str) -> Solution:
        string = string.lower()
        if "unsat" in string:
            return (False, [])

        def is_int(s):
            return s.isdigit() or (s[0] == '-' and s[1:].isdigit())

        ints = [int(s) for s in string.split() if is_int(s)]
        ids = [i for i in ints if i != 0]
        return (True, ids)
