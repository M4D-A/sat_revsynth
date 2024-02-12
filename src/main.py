from collection_synthesizer.collection_synthesizer import CollectionSynthesizer
from dimgroup_synthesizer.dimgroup_synthesizer import DimGroup

cs = CollectionSynthesizer(4, 5)
collection = cs.synthesize()

for width, width_subcollection in enumerate(collection):
    for gc, dimgroup in enumerate(width_subcollection):
        print(f"({width}, {gc}): {len(dimgroup)}")
    print()
