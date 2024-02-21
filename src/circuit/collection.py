from circuit.dim_group import DimGroup


class Collection:
    def __init__(self, max_width: int, max_gate_count: int):
        mw = max_width
        mgc = max_gate_count
        self._max_width = mw
        self._max_gate_count = mgc
        self._groups = [
            [DimGroup(width, gc) for gc in range(mgc + 1)] for width in range(mw + 1)
        ]

    def __len__(self) -> int:
        return len(self._groups)

    def __getitem__(self, key: int) -> list[DimGroup]:
        return self._groups[key]
