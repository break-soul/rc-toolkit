"""
Store the enums used in the package.
"""
from enum import Enum

class _MISSING_TYPE:
    pass

MISSING = _MISSING_TYPE()

class System(Enum):
    Other = 0
    AIX = 1
    Linux = 2
    Win32 = 3
    Cygwin = 4
    macOS = 5
    FreeBSD = 6

class In_Enum(Enum):
    File = 0
