from collection_synthesizer.collection_synthesizer import CollectionSynthesizer

cs = CollectionSynthesizer(4, 6)
collection = cs.synthesize()

for width, width_subcollection in enumerate(collection):
    for gc, dimgroup in enumerate(width_subcollection):
        print(f"({width}, {gc}): {len(dimgroup)}")
    print()
