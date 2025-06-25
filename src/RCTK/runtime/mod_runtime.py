import os
import sys
from functools import lru_cache
from typing import Optional
from ..tk_io.file import get_name


@lru_cache(1)
def log():
    from logging import getLogger

    return getLogger("RCTK.Utils.ModRuntime")


def add_path(path: str):
    sys.path.append(path)


def remove_path(path: str):
    sys.path.remove(path)


def hook_builtin(key: str, value: object):
    from ..core.tk_api import tk_1

    log().warning(f"Hooking builtin {key} as {value.__str__()}")
    tk_1.tk_100000(key, value)


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
