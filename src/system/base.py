import platform
from enum import Enum
from functools import lru_cache


from ..base.enums import System


class System(Enum):
    Other = "other"
    AIX = "aix"
    Linux = "linux"
    Win32 = "win32"
    Cygwin = "cygwin"
    macOS = "darwin"
    FreeBSD = "freebsd"

    @lru_cache(1)
    @classmethod
    def get_os(cls, os_str: str = platform.system()) -> "System":
        if os_str == "win32":
            return cls.Win32
        if os_str == "linux":
            return cls.Linux
        if os_str == "darwin":
            return cls.macOS
        if os_str == "aix":
            return cls.AIX
        if os_str == "cygwin":
            return cls.Cygwin
        if os_str.startswith("freebsd"):
            return cls.FreeBSD
        return cls.Other

class Arch(Enum):
    x86 = "x86"
    x64 = "x64"
    ARM = "arm"
    ARM64 = "arm64"
    Other = "other"

    @lru_cache(1)
    @classmethod
    def get_arch(cls, arch_str: str = platform.machine()) -> "Arch":
        if arch_str == "AMD64":
            return cls.x64
        if arch_str == "x86":
            return cls.x86
        if arch_str == "ARM":
            return cls.ARM
        if arch_str == "ARM64":
            return cls.ARM64
        
    
env_os = System.get_os()
