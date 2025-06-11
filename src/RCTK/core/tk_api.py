
try:
    from .tk_core_api import *
except:
    from tk_core_api import * # type: ignore
    raise
