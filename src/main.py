from collection_synthesizer.collection_synthesizer import CollectionSynthesizer
from dimgroup_synthesizer.dimgroup_synthesizer import DimGroupSynthesizer

cs = CollectionSynthesizer(3, 5)
collection = cs.synthesize(16)

for w, wsc in enumerate(collection):
    for gc, dimg in enumerate(wsc):
        print(f"({w}, {gc}): {len(dimg)}")
