from collection_synthesizer.collection_synthesizer import CollectionSynthesizer
from dimgroup_synthesizer.dimgroup_synthesizer import DimGroupSynthesizer
import sys

cs = CollectionSynthesizer(3, 8)
collection = cs.synthesize(16)
