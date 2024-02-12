from truth_table.truth_table import TruthTable
from sat.solver import Solver
from synthesizer.synthesizer import Synthesizer
from dimgroup_synthesizer.dimgroup_synthesizer import DimGroupSynthesiser

dgs = DimGroupSynthesiser(3, 4)
circuits = dgs.synthesise()
print(len(circuits))
