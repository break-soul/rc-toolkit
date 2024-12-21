"""
This module contains functions to control the Python interpreter.
"""

import os
import sys
import importlib.util

from typing import NoReturn, TYPE_CHECKING

from rclog import get_log

from .control import lazy_load

if TYPE_CHECKING:
    from logging import Logger


class Env:
    @staticmethod
    def set_env(key: str, value: str) -> None:
        os.environ[key] = value

    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> str:
        return os.environ.get(key, default)

    @staticmethod
    @lazy_load
    def is_debug() -> bool:
        """
        Check whether it == DEBUG mode

        Returns:
            bool: __debug__
        """
        return bool(Env.get_env("DEBUG", default=0))

@lazy_load
def log() -> "Logger":
    return get_log("RCTK.base.pycontrol")


def get_pycache() -> str:
    return sys.pycache_prefix()


def add_path(path: str) -> NoReturn:
    sys.path.append(path)


def remove_path(path: str) -> NoReturn:
    sys.path.remove(path)


class Compile:

    @staticmethod
    def compile_file(
        file, cfile=None, dfile=None, doraise=False, optimize=1, quiet=0
    ) -> None:
        log.info("Compile {file}".format(file=file))
        import py_compile

    @staticmethod
    def compile_dir(
        path, cfile=None, dfile=None, doraise=False, optimize=1, quiet=0
    ) -> None:
        Compile.compile_file(file)


def set_global(key: str, value: object) -> NoReturn:
    import builtins

    log().warning("Hooking builtin {} as {}".format(key, str(value)))
    builtins.__dict__[key] = value


def is_module(name, path: str) -> bool: ...


def get_module(path: str) -> object: ...


def exit_py() -> NoReturn:
    sys.exit()
