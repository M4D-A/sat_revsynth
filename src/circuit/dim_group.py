from circuit.circuit import Circuit


class DimGroup:
    def __init__(self, width: int, gate_count: int):
        self._width = width
        self._gate_count = gate_count
        self._circuits = []

    def __len__(self) -> int:
        return len(self._circuits)

    def __getitem__(self, key: int) -> Circuit:
        return self._circuits[key]

    def __bool__(self) -> bool:
        return bool(self._circuits)

    def extend(self, other: "DimGroup"):
        assert (self._width, self._gate_count) == (other._width, other._gate_count)
        self._circuits += other._circuits
