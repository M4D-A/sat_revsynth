from copy import deepcopy, copy


def inplace(method):
    def wrap(self, *a, **k):
        inplace = k.pop("inplace", True)
        if inplace:
            method(self, *a, **k)
        else:
            return method(copy(self), *a, **k)
    return wrap
