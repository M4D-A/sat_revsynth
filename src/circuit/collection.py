from circuit.dim_group import DimGroup


class Collection:
    def __init__(self, max_width: int, max_gate_count: int):
        self._max_width = max_width
        self._max_gate_count = max_gate_count
        self._groups = [
            [DimGroup(width, gc) for gc in range(max_gate_count + 1)] for width in range(max_width + 1)
        ]

    def __len__(self) -> int:
        return len(self._groups)

    def __getitem__(self, key: int) -> list[DimGroup]:
        return self._groups[key]
