from synthesizers.collection_synthesizer import CollectionSynthesizer

cs = CollectionSynthesizer(3, 5)
cs.set_file_save("/home/adam/data", "test_1")
collection = cs.synthesize(16)

for wsc in collection:
    for dg in wsc:
        print(f"({dg._width}, {dg._gate_count}): {len(dg)}")

# ecd = ExCircDistiller(collection)
# exc_collection = ecd.distill()
#
# print("-------")
# for w, wsc in enumerate(exc_collection):
#     for gc, dimg in enumerate(wsc):
#         print(f"({w}, {gc}): {len(dimg)}")
        # for circ in dimg:
        #     print(circ)
