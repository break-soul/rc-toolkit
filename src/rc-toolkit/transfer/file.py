"""
File IO module
"""

from os import path, makedirs
from pathlib import Path
from typing import NoReturn


def get_dir() -> tuple: ...


def mkdir(file_path: str) -> NoReturn:
    """
    make log file dirs

    Args:
        file_path (str): file path
    """

    dir_path = Path(file_path).parent
    if not path.isdir(dir_path):
        try:
            makedirs(dir_path)
        except Exception:  # pylint: disable=broad-exception-caught
            raise


def try_open():
    """
    try to open file
    """
    
    try:
        with open() as file:
            pass
    except Exception:  # pylint: disable=broad-exception-caught
        raise


def try_read():
    """
    try to read file
    """
    
    try:
        with open() as file:
            pass
    except Exception:  # pylint: disable=broad-exception-caught
        raise
