from collection_synthesizer.collection_synthesizer import CollectionSynthesizer
from dimgroup_synthesizer.dimgroup_synthesizer import DimGroup
from sat.cnf import CNF

cs = CollectionSynthesizer(3, 6)
collection = cs.synthesize()

for width, width_subcollection in enumerate(collection):
    for gc, dimgroup in enumerate(width_subcollection):
        print(f"({width}, {gc}): {len(dimgroup)}")
    print()

print(CNF.app_time)
print(CNF.lcomp_time)
print(CNF.ex_time)
