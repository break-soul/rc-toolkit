"""
This module contains functions to control the Python interpreter.
"""

import os
import sys
import py_compile

from typing import Optional,TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

def log() -> "Logger":
    from .logger import get_log
    return get_log("RCTK.Core.Env")


class Env:
    @staticmethod
    def set_env(key: str, value: str) -> None:
        os.environ[key] = value

    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> str:
        return os.environ.get(key, default)

    @staticmethod
    def is_debug() -> bool:
        """
        Check whether it == DEBUG mode

        Returns:
            bool: __debug__
        """
        return bool(Env.get_env("DEBUG", default=0))

is_debug = Env.is_debug

def get_pycache() -> str:
    return sys.pycache_prefix()

def is_module(name, path: str) -> bool:
    return os.path.isfile(os.path.join(path, name))

def get_module(path: str) -> object:
    import importlib.util
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def exit_py():
    sys.exit()
