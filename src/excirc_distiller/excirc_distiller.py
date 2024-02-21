from circuit.circuit import Circuit
from synthesizers.collection_synthesizer import Collection

ExcDimGroup = list[Circuit]
ExcCollection = list[list[ExcDimGroup]]


class ExCircDistiller:
    def __init__(self, collection: Collection):
        self._collection: Collection = collection
        self._max_width: int = len(collection) - 1
        self._max_gc: int = len(collection[0]) - 1
        self._max_ext_gc = self._max_gc // 2 + 1
        assert all(len(subcoll) == self._max_gc + 1 for subcoll in collection)

    def distill(self):
        self._raw_excirc_collection()
        return self._excirc_collection

    def _raw_excirc_collection(self):
        exc_collection: ExcCollection = []
        for width in range(self._max_width + 1):
            width_subcollection = [[], ]
            for gc in range(0, self._max_gc + 1, 2):
                dimgroup_a = self._collection[width][gc]
                dimgroup_b = self._collection[width][gc + 1]
                exc_dg_a = [circ.min_slice() for circ in dimgroup_a]
                exc_dg_b = [circ.min_slice() for circ in dimgroup_b]
                exc_dg = Circuit.filter_duplicates(exc_dg_a + exc_dg_b)
                width_subcollection.append(exc_dg)
            exc_collection.append(width_subcollection)
        self._excirc_collection = exc_collection
