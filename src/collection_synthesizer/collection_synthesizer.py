from circuit.circuit import Circuit
from dimgroup_synthesizer.dimgroup_synthesizer import DimGroupSynthesiser, DimGroup
from itertools import product

Collection = list[list[DimGroup]]


class CollectionSynthesizer:
    def __init__(self, max_width: int, max_gate_count: int):
        self._max_width = max_width
        self._max_gate_count = max_gate_count
        self._collection: Collection = [
            [[] for _ in range(max_gate_count)]
        ]

    def synthesize(self) -> Collection:
        for width in range(1, self._max_width + 1):
            set_width_subcollection = [[], []]  # gc in {0,1}
            self._collection.append(set_width_subcollection)
            for gc in range(2, self._max_gate_count + 1):
                trivial = self._construct_from_previous(width, gc)
                print(width, gc, len(trivial))
                dgs = DimGroupSynthesiser(width, gc)
                dimgroup = dgs.synthesise(trivial)
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
