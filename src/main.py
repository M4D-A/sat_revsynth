from truth_table.truth_table import TruthTable
from synthesizers.optimal_synthesizer import OptimalSynthesizer
from sat.solver import Solver
from tqdm import tqdm
from random import shuffle

bits = 4

max_gc = 12
table_size = pow(2, bits)
input_table = list(range(table_size))
inputs = []
for i in range(10):
    shuffle(input_table)
    inputs.append(input_table[:])


solvers = ["minisat-gh", "kissat"]

for s in solvers:
    solver = Solver(s)
    histogram = [0] * (max_gc + 1)
    fails = 0

    for permutation in tqdm(inputs):
        tt = TruthTable(bits, list(permutation))
        os = OptimalSynthesizer(tt, 0, max_gc, solver)
        qc = os.solve()
        if qc is not None:
            qc_size = len(qc)
            histogram[qc_size] += 1
        else:
            fails += 1
        print(qc)

    print(f"Histo: {histogram}")
    print(f"Fails: {fails}")
    print()
