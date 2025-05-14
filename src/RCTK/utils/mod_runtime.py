
import sys
from functools import lru_cache

@lru_cache(1)
def log():
    from logging import getLogger
    return getLogger("RCTK.Utils.ModRuntime")

def add_path(path: str):
    sys.path.append(path)

def remove_path(path: str):
    sys.path.remove(path)

def hook_builtin(key: str, value: object):
    import builtins
    log().warning(f"Hooking builtin {key} as {value.__str__()}")
    builtins.__dict__[key] = value
