from random import randint, sample


def x_params(bits_num):
    target = randint(0, bits_num - 1)
    return target


def cx_params(bits_num):
    control, target = sample(range(0, bits_num - 1), 2)
    return control, target


def mcx_params(bits_num):
    special_ids_num = randint(2, bits_num - 1)
    target, *controls = sample(range(0, bits_num - 1), special_ids_num)
    return controls, target
