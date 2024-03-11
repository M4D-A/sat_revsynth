from circuit.circuit import Circuit, Gate
from circuit.collection import Collection


def gate_dump_str(gate: Gate) -> str:
    controls, target = gate
    gate_str = f"{target}"
    if controls:
        gate_str += " " + " ".join(str(c) for c in controls)
    return gate_str


def circuit_dump_str(circuit: Circuit) -> str:
    circuit_str = f"c {circuit.width()} {len(circuit)}\n"
    for gate in circuit.gates():
        circuit_str += gate_dump_str(gate) + "\n"
    return circuit_str


def collection_dump_str(collection: Collection) -> str:
    mw = collection._max_width
    mgc = collection._max_gate_count
    collection_str = f"h {mw} {mgc}\n\n"
    for w in range(mw + 1):
        for gc in range(mgc + 1):
            for circuit in collection[w][gc]:
                circuit_str = circuit_dump_str(circuit)
                collection_str += circuit_str + "\n"

    return collection_str
