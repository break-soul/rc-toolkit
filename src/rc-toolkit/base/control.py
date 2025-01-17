"""
This module contains functions to control the Python interpreter.
"""

import os
import sys
import builtins
import py_compile

from typing import NoReturn, TYPE_CHECKING, Optional

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
    return get_log("RCTK.base.control")


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
        py_compile.compile(file, cfile, dfile, doraise, optimize, quiet)

    @staticmethod
    def compile_dir(
        path, cfile=None, dfile=None, doraise=False, optimize=1, quiet=0
    ) -> None:
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    Compile.compile_file(
                        os.path.join(root, file), cfile, dfile, doraise, optimize, quiet
                    )


def set_global(key: str, value: object) -> NoReturn:
    log().warning(f"Hooking builtin {key} as {value}")
    builtins.__dict__[key] = value


def is_module(name, path: str) -> bool:
    return os.path.isfile(os.path.join(path, name))


def get_module(path: str) -> object:
    import importlib.util

    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exit_py() -> NoReturn:
    sys.exit()
