from circuit.dim_group import DimGroup
from itertools import product
from copy import copy


class Collection():
    def __init__(self, max_width: int, max_gate_count: int):
        self._max_width = max_width
        self._max_gate_count = max_gate_count
        self._w_iter = range(max_width + 1)
        self._gc_iter = range(max_gate_count + 1)
        self._group_ids_iter = product(self._w_iter, self._gc_iter)
        self._groups = [
            [DimGroup(width, gc) for gc in self._gc_iter] for width in self._w_iter
        ]

    def __len__(self) -> int:
        return len(self._groups)

    def __getitem__(self, key: int) -> list[DimGroup]:
        return self._groups[key]

    def __str__(self) -> str:
        string = ""
        for width, gc in copy(self._group_ids_iter):
            dimg = self[width][gc]
            string += f"({width}, {gc}): {len(dimg)}\n"
        return string

    def fill_empty_line_extensions(self) -> "Collection":
        extensions = self._empty_line_extensions()
        self.join(extensions)
        return self

    def fill_full_line_extensions(self) -> "Collection":
        extensions = self._full_line_extensions()
        self.join(extensions)
        return self

    def remove_reducibles(self) -> "Collection":
        for width, reducing_gc in copy(self._group_ids_iter):
            reducing_dg = self[width][reducing_gc]
            for reducted_gc in range(reducing_gc + 1, self._max_gate_count + 1):
                reducted_dg = self[width][reducted_gc]
                reducted_dg.remove_reducibles(reducing_dg)
        return self

    def _empty_line_extensions(self) -> "Collection":
        extensions = Collection(self._max_width, self._max_gate_count)
        for width, gc in copy(self._group_ids_iter):
            dimgroup = self[width][gc]
            for circ in dimgroup:
                for target_width in range(width + 1, self._max_width + 1):
                    new_extensions = circ.empty_line_extensions(target_width)
                    extensions[target_width][gc].extend(new_extensions)
        return extensions

    def _full_line_extensions(self) -> "Collection":
        extensions = Collection(self._max_width, self._max_gate_count)
        for width, gc in copy(self._group_ids_iter):
            dimgroup = self[width][gc]
            for circ in dimgroup:
                for target_width in range(width + 1, self._max_width + 1):
                    new_extensions = circ.full_line_extensions(target_width)
                    extensions[target_width][gc].extend(new_extensions)
        return extensions

    def _validate_collection(self, other: "Collection") -> None:
        assert (self._max_width, self._max_gate_count) == (other._max_width, other._max_gate_count)

    def join(self, other: "Collection") -> None:
        self._validate_collection(other)
        for width, gc in copy(self._group_ids_iter):
            self[width][gc].join(other[width][gc])
