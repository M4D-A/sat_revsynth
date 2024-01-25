from pysat.solvers import Cadical153, Lingeling, Glucose4
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE
from .cnf import CNF, Literal

Solution = tuple[bool, list[int]]

class Solver:
    external_solvers = {
        "kissat": [],
        # "cms":["--verb", "0"],
        # "parkissat": ["-v=1", "-c=8", "-max-memory=8"]
    }

    builtin_solvers = {
        "cadical": Cadical153,
        "lingeling": Lingeling,
        "glucose4": Glucose4
    }
    
    available_solvers = list(external_solvers.keys()) + list(builtin_solvers.keys())

    def __init__(self, name: str, args = None):
        if name not in Solver.available_solvers:
            raise ValueError(f"Solver {name} not supported")
        self.__name = name
        self.__args = args

    def solve(self, cnf: CNF):
        if self.__name in self.builtin_solvers:
            solution = self._solve_builtin(cnf)
        elif self.__name in self.external_solvers:
            solution = self._solve_external(cnf)
        else:
            raise ValueError(f"Solver {self.__name} not supported")
        return self._make_model(solution, cnf)
 
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
        with NamedTemporaryFile(dir=".") as f:
            cnf.to_file(f.name)
            p = Popen([self.__name, f.name, *args], stdout=PIPE, stderr=PIPE)
            out, _ = p.communicate()
        string = out.decode('utf-8').lower()
        if "unsat" in string:
            return (False, [])
        else:
            ids = self._extract_ints(string)
            return (True, ids)

    @staticmethod
    def _make_model(solution: Solution, cnf: CNF):
        sat, ids = solution
        if not sat:
            return {"sat": False}

        model_dict = {
            "sat" : sat
        }
        for id in ids:
            if cnf.check_id(id): 
                literal = cnf.id_to_literal(id)
                name = literal.name()
                model_dict[name] = bool(literal)
        return model_dict

    @staticmethod
    def _extract_ints(string: str) -> list[int]:
        ints = [int(s) for s in string.split() if s.isdigit() or (s[0] == '-' and s[1:].isdigit())]
        return [i for i in ints if i != 0]   

        
