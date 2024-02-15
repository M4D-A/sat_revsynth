from circuit.circuit import Circuit
from dimgroup_synthesizer.dimgroup_synthesizer import DimGroupSynthesizer, DimGroup
from itertools import product
from timeit import default_timer as timer

Collection = list[list[DimGroup]]


class CollectionSynthesizer:
    def __init__(self, max_width: int, max_gate_count: int):
        self._max_width = max_width
        self._max_gate_count = max_gate_count
        self._collection: Collection = [
            [[] for _ in range(max_gate_count)]
        ]

    def synthesize(self, threads_num: int = 1) -> Collection:
        for width in range(1, self._max_width + 1):
            set_width_subcollection = [[], []]  # gc in {0,1}
            self._collection.append(set_width_subcollection)
            for gc in range(2, self._max_gate_count + 1):
                start = timer()
                dgs = DimGroupSynthesizer(width, gc)
                print()
                print(f"(W, GC) = ({width}, {gc})")
                print("-----------------------------------------")
                dimgroup = dgs.synthesize_mt(threads_num)
                dgs_time = timer() - start
                print("-----------------------------------------")
                print(f"TOTAL RT:       {dgs_time:6.2f}s -- {len(dimgroup):7} circuits")
                set_width_subcollection.append(dimgroup)
        return self._collection

    def _construct_from_previous(self, width: int, gc: int) -> list[Circuit]:
        generated = []
        if gc >= 4:
            for left_gc in range(2, gc - 1):
                right_gc = gc - left_gc
                left_dimgroup = self._collection[width][left_gc]
                right_dimgroup = self._collection[width][right_gc]
                for left_gate, right_gate in product(left_dimgroup, right_dimgroup):
                    generated.append(left_gate + right_gate)
        unrolled = []
        for circuit in generated:
            unrolled += circuit.unroll()
        return Circuit.filter_duplicates(unrolled)
