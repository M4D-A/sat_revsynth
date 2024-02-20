from circuit.circuit import Circuit
from circuit.collection import Collection
from synthesizers.dimgroup_synthesizer import DimGroupSynthesizer
from itertools import product
from timeit import default_timer as timer
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
                start = timer()
                print()
                print(f"(W, GC) = ({width}, {gc})")
                print("-----------------------------------------")
                dimgroup = dgs.synthesize_mt(threads_num)
                dgs_time = timer() - start
                print("-----------------------------------------")
                print(f"TOTAL RT:       {dgs_time:6.2f}s -- {len(dimgroup):7} circuits")
                self._collection._groups[width][gc] = dimgroup
                if self._save:
                    with open(f"{self._file_prefix}_{width}_{gc}.pickle", "wb") as f:
                        dump(self._collection, f)
        return self._collection

    def set_file_save(self, dir: str, collection_name: str):
        self._dir = dir
        self._collection_name = collection_name
        self._file_prefix = join(dir, collection_name)
        self._save = True

    def _construct_from_previous(self, width: int, gc: int) -> list[Circuit]:
        generated = []
        if gc >= 4:
            for left_gc in range(2, gc - 1):
                right_gc = gc - left_gc
                left_dimgroup = self._collection._groups[width][left_gc]
                right_dimgroup = self._collection._groups[width][right_gc]
                for left_gate, right_gate in product(left_dimgroup._circuits, right_dimgroup._circuits):
                    generated.append(left_gate + right_gate)
        if len(generated) > 0:
            generated = generated[0].unroll(generated)
        return generated
