import os
import sys
from functools import lru_cache

from typing import Optional

from ..base.enums import System


def get_os() -> System:
    if sys.platform == "win32":
        return System.Win32
    if sys.platform == "linux":
        return System.Linux
    if sys.platform == "darwin":
        return System.macOS
    if sys.platform == "aix":
        return System.AIX
    if sys.platform == "cygwin":
        return System.Cygwin
    if sys.platform.startswith("freebsd"):
        return System.FreeBSD
    return System.Other


class Env:
    @staticmethod
    def set_env(key: str, value: str) -> None:
        os.environ[key] = value

    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> str:
        return os.environ.get(key, default)

    @staticmethod
    @lru_cache(4)
    def is_debug() -> bool:
        """
        Check whether it == DEBUG mode

        Returns:
            bool: __debug__
        """
        return bool(Env.get_env("DEBUG", default=0))
