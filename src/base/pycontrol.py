"""
This module contains functions to control the Python interpreter.
"""
import sys

from typing import NoReturn

def get_pycache() -> str:
    return sys.pycache_prefix

def add_path(path: str) -> NoReturn:
    sys.path.append(path)

def remove_path(path: str) -> NoReturn:
    sys.path.remove(path)

def exit_py() -> NoReturn:
    sys.exit()
