from circuit.collection import Collection
from synthesizers.dimgroup_synthesizer import DimGroupSynthesizer
from pickle import dump
from os.path import join


class CollectionSynthesizer:
    def __init__(self, max_width: int, max_gate_count: int):
        self._max_width = max_width
        self._max_gate_count = max_gate_count
        self._collection = Collection(max_width, max_gate_count)

    def synthesize(self, threads_num: int = 1) -> Collection:
        for width in range(1, self._max_width + 1):
            for gc in range(2, self._max_gate_count + 1):
                dgs = DimGroupSynthesizer(width, gc)
                dimgroup = dgs.synthesize_mt(threads_num)
                self._collection[width][gc] = dimgroup
                if self._save:
                    with open(f"{self._file_prefix}_{width}_{gc}.pickle", "wb") as f:
                        dump(self._collection, f)
        return self._collection

    def set_file_save(self, dir: str, collection_name: str) -> None:
        self._dir = dir
        self._collection_name = collection_name
        self._file_prefix = join(dir, collection_name)
        self._save = True
