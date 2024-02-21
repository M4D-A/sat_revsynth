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

    def append(self, other: Circuit):
        msg = f"({self._width}, {self._gate_count}) != ({other._width}, {len(other)})"
        assert (self._width, self._gate_count) == (other._width, len(other)), msg
        self._circuits.append(other)

    def extend(self, other: list[Circuit]):
        for circ in other:
            self.append(circ)

    def join(self, other: "DimGroup"):
        msg = f"({self._width}, {self._gate_count}) != ({other._width}, {other._gate_count})"
        assert (self._width, self._gate_count) == (other._width, other._gate_count), msg
        self._circuits += other._circuits
