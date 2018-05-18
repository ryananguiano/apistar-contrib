try:
    import pytz
except ImportError:
    pytz = None


import random
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False
