from excirc_distiller.excirc_distiller import ExCircDistiller
from pickle import load

# cs = CollectionSynthesizer(4, 7)
# cs.set_file_save("/home/adam/data", "test")
# collection = cs.synthesize(16)

with open("/home/adam/data/test_3_7.pickle", "rb") as f:
    collection = load(f)

ecd = ExCircDistiller(collection)
exc_collection = ecd.distill()
print()
print("----------")
print(exc_collection)
