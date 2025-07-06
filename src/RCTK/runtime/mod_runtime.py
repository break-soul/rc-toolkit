import os
import sys
from functools import lru_cache
from typing import Optional
from ..tk_io.file import get_name
from typing import TYPE_CHECKING, overload

@lru_cache(1)
def log():
    from logging import getLogger

    return getLogger("RCTK.Utils.ModRuntime")

@overload
def add_path(path: str): ...
@overload
def add_path(path: str, *any_path): ...
def add_path(*args: list, **kw): # type: ignore
    args.extend(kw.get("path", [])) # type: ignore
    if len(args) <= 0: raise ValueError("Missing args!")
    args_ = [str(x) for x in args]
    sys.path.extend(args_)


def remove_path(path: str):
    sys.path.remove(path)

def _hook_buildin(key: str, value: object):
    import builtins
    builtins.__dict__[key] = value


def hook_builtin(key: str, value: object):
    log().warning(f"Hooking builtin {key} as {value.__str__()}")
    _hook_buildin(key, value)


def load_pyd(file_path: str, name: Optional[str] = None) -> object:
    import importlib.util as imp_u

    if name is None:
        name = str(get_name(file_path)[0]).split(".")[0]

    if file_path and os.path.exists(file_path):
        if spec := imp_u.spec_from_file_location(name, file_path):
            main = imp_u.module_from_spec(spec)
            spec.loader.exec_module(main)  # type: ignore
            return main
        else:
            raise ImportError(f"Cannot load {file_path} as a module")
    else:
        raise FileNotFoundError(f"File {file_path} does not exist")
