from importlib import import_module


def load_class(import_string: str) -> type:
    abs_module_path, class_name = import_string.rsplit('.', 1)
    module_object = import_module(abs_module_path)
    target_class = getattr(module_object, class_name)
    assert isinstance(target_class, type)
    return target_class


# pytz
try:
    import pytz
except ImportError:
    pytz = None


# redis
try:
    import redis
except ImportError:
    redis = None


# pickle
try:
    import cPickle as pickle
except ImportError:
    import pickle
PICKLE_VERSION = -1


# random
import random
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False
