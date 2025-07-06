"""
This module contains functions to control the Python interpreter.
"""

import os
import sys
import py_compile

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


def log() -> "Logger":
    from .logger import get_log

    return get_log("RCTK.Core.Env")


class Env:
    @staticmethod
    def add_path(path: str) -> None:
        Env.set_env("path", Env.get_env("path") + ";" + path)  # type: ignore

    @staticmethod
    def set_env(key: str, value: str) -> None:
        os.environ[key] = value

    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        return (
            os.environ.get(key, default) if default is not None else os.environ.get(key)
        )

    @staticmethod
    def is_debug() -> bool:
        return bool(Env.get_env("DEBUG", default="False"))


is_debug = Env.is_debug


def get_pycache() -> Optional[str]:
    return sys.pycache_prefix


class Compile:
    @staticmethod
    def compile_file(
        file, cfile=None, dfile=None, doraise=False, optimize=1, quiet=0
    ) -> None:
        log().info("Compile {file}".format(file=file))
        py_compile.compile(file, cfile, dfile, doraise, optimize, quiet)  # type: ignore

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


def is_module(name, path: str) -> bool:
    return os.path.isfile(os.path.join(path, name))


def exit_py():
    sys.exit()
