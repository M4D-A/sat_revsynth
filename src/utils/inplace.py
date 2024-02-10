from copy import copy


def inplace(method):
    def wrap(self, *a, **k):
        inplace = k.pop("inplace", True)
        if inplace:
            return method(self, *a, **k)
        else:
            return method(copy(self), *a, **k)
    return wrap
