from synthesizers.collection_synthesizer import CollectionSynthesizer
from excirc_distiller.excirc_distiller import ExCircDistiller

cs = CollectionSynthesizer(3, 7)
collection = cs.synthesize(16)

ecd = ExCircDistiller(collection)
exc_collection = ecd.distill()
print()
print("----------")
print(exc_collection)
