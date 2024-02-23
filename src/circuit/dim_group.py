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

    def _validate_circuit(self, circuit: Circuit) -> None:
        msg = f"({self._width}, {self._gate_count}) != ({circuit._width}, {len(circuit)})"
        assert (self._width, self._gate_count) == (circuit._width, len(circuit)), msg

    def _validate_dimgroup(self, other: "DimGroup") -> None:
        msg = f"({self._width}, {self._gate_count}) != ({other._width}, {other._gate_count})"
        assert (self._width, self._gate_count) == (other._width, other._gate_count), msg

    def append(self, circuit: Circuit) -> None:
        self._validate_circuit(circuit)
        self._circuits.append(circuit)

    def extend(self, other: list[Circuit]) -> None:
        for circ in other:
            self.append(circ)

    def join(self, other: "DimGroup") -> None:
        self._validate_dimgroup(other)
        self._circuits += other._circuits

    def remove_reducibles(self, reductors: "DimGroup"):
        assert reductors._width == self._width
        assert reductors._gate_count < self._gate_count
        irreducible = [circ for circ in self._circuits if not circ.reducible(reductors._circuits)]
        self._circuits = irreducible
