
from functools import partial

from ..core.logger import get_log
log = partial(get_log, "RCTK.Runtime.PyENV")

def _hook_buildin(key: str, value: object):
    import builtins
    builtins.__dict__[key] = value


def hook_builtin(key: str, value: object):
    log().warning(f"Hooking builtin {key} as {value.__str__()}")
    _hook_buildin(key, value)

class LazyImport:
    ...

def lazy_import():...

def mod_import(global_ = globals(), import_ = lazy_import):
    ...