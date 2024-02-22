from synthesizers.collection_synthesizer import CollectionSynthesizer
from excirc_distiller.excirc_distiller import ExCircDistiller

cs = CollectionSynthesizer(3, 5)
cs.set_file_save("/home/adam/data", "test_1")
collection = cs.synthesize(16)
print(collection)


ecd = ExCircDistiller(collection)
exc_collection = ecd.distill()
print()
print("----------")
print(exc_collection)
