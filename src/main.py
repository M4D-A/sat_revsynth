from synthesizers.collection_synthesizer import CollectionSynthesizer
from excirc_distiller.excirc_distiller import ExCircDistiller

cs = CollectionSynthesizer(3, 6)
cs.set_file_save("/home/adam/data", "test_1")
collection = cs.synthesize(16)

for wsc in collection:
    for dg in wsc:
        print(f"({dg._width}, {dg._gate_count}): {len(dg)}")

ecd = ExCircDistiller(collection)
exc_collection = ecd.distill()

print("-------")
for w, wsc in enumerate(exc_collection):
    for gc, dimg in enumerate(wsc):
        print(f"({w}, {gc}): {len(dimg)}")
