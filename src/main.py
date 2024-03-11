from excirc_distiller.excirc_distiller import ExCircDistiller
from synthesizers.collection_synthesizer import CollectionSynthesizer
# from utils.dump import circuit_dump_str, collection_dump_str
# from pickle import load

# with open("/home/adam/data/test_3_7.pickle", "rb") as f:
#     collection = load(f)

sy = CollectionSynthesizer(3, 5)
collection = sy.synthesize()
print(collection)

exc = ExCircDistiller(collection)

exc_coll = exc.distill()
print(exc_coll)

# with open("/home/adam/dump_3_5.txt", "w") as f:
#     f.write(collection_dump_str(exc_coll))
