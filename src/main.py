from sbox.sbox import Sbox
from random import shuffle

bits = 4
size = 2**bits

table = list(range(size))

counter = [0] * (bits + 1)
for i in range(100_000):
    shuffle(table)
    sbox = Sbox(bits, table)
    d1 = sbox.algebraic_degree()
    counter[d1] += 1
    if ((i + 1) % 10_000) == 0:
        print(counter)


print(counter)
