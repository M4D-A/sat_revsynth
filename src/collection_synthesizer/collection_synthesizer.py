from dimgroup_synthesizer.dimgroup_synthesizer import DimGroupSynthesiser, DimGroup

CircuitsCollection = list[list[DimGroup]]


class CollectionSynthesizer:
    def __init__(self, max_width: int, max_gate_count: int):
        self._max_width = max_width
        self._max_gate_count = max_gate_count

    def synthesize(self) -> CircuitsCollection:
        collection: CircuitsCollection = [
            []  # width = 0
        ]
        for width in range(1, self._max_width + 1):
            set_width_subcollection = [[], []]  # gc in {0,1}
            for gc in range(2, self._max_gate_count + 1):
                dgs = DimGroupSynthesiser(width, gc)
                dimgroup = dgs.synthesise()
                set_width_subcollection.append(dimgroup)
            collection.append(set_width_subcollection)
        return collection
