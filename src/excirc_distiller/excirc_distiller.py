from synthesizers.collection_synthesizer import Collection


class ExCircDistiller:
    def __init__(self, collection: Collection):
        self._collection: Collection = collection
        self._max_width: int = collection._max_width
        self._max_gate_count: int = collection._max_gate_count
        self._max_exc_gc = self._max_gate_count // 2 + 1

    def distill(self):
        print("0. REC started")
        excircuits = self._raw_excirc_collection()
        print()
        print("1. REC finished - FEL started")
        excircuits.fill_empty_line_extensions()
        print()
        print("2. FEL finished - FFL started")
        excircuits.fill_full_line_extensions()
        print()
        print("3. FFL finished - RMR started")
        excircuits.remove_reducibles()
        print()
        print("4. RMR finished - RMD started")
        excircuits.remove_duplicates()
        print()
        print("5. RMD finished")
        return excircuits

    def _raw_excirc_collection(self):
        excircuits = Collection(self._max_width, self._max_exc_gc)
        for width in range(self._max_width + 1):
            for exc_gc in range(1, self._max_exc_gc + 1):
                print(f"  -- REC({width}, {exc_gc})")
                gc = (exc_gc - 1) * 2
                dimgroup_a = self._collection[width][gc]
                ext_list_a = [circ.min_slice() for circ in dimgroup_a]
                dimgroup_b = (
                    self._collection[width][gc + 1] if gc < self._max_gate_count else []
                )
                ext_list_b = [circ.min_slice() for circ in dimgroup_b]
                ext_list = ext_list_a + ext_list_b
                excircuits[width][exc_gc]._circuits = ext_list
        return excircuits
