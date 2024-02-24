from synthesizers.collection_synthesizer import CollectionSynthesizer
from excirc_distiller.excirc_distiller import ExCircDistiller
from pickle import load

# cs = CollectionSynthesizer(3, 7)
# cs.set_file_save("/home/adam/data", "test_1")
# collection = cs.synthesize(16)

with open("/home/adam/data/test_1_3_7.pickle", "rb") as f:
    collection = load(f)
# print(collection)

ecd = ExCircDistiller(collection)
exc_collection = ecd.distill()
print()
print("----------")
print(exc_collection)
