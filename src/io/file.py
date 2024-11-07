"""
File IO module
"""
from os import path, makedirs
from pathlib import Path

from typing import NoReturn

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


