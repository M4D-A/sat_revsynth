from circuit.collection import Collection
from truth_table.truth_table import TruthTable
from synthesizers.optimal_synthesizer import OptimalSynthesizer
from sat.solver import Solver

c = Collection(4, 4).from_file("/home/adam/exc_4_7.txt")
# print(c)

elephant_sbox = [
    0x0E, 0x0D, 0x0B, 0x00, 0x02, 0x01, 0x04, 0x0F,
    0x07, 0x0A, 0x08, 0x05, 0x09, 0x0C, 0x03, 0x06
]
photon_beatle_sbox = [
    0x0C, 0x05, 0x06, 0x0B, 0x09, 0x00, 0x0A, 0x0D,
    0x03, 0x0E, 0x0F, 0x08, 0x04, 0x07, 0x01, 0x02
]

tt = TruthTable(4, elephant_sbox)

print(tt.values())
os = OptimalSynthesizer(tt, 0, 11, Solver("kissat"))
os.exclude_collection(c)
cq = os.solve()

print(cq)
