import platform
from enum import Enum
from functools import lru_cache


class System(Enum):
    Other = "other"
    AIX = "aix"
    Linux = "linux"
    Win32 = "win32"
    Cygwin = "cygwin"
    macOS = "darwin"
    FreeBSD = "freebsd"

    @classmethod
    @lru_cache(1)
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
    x86 = "i386"
    x64 = "amd64"
    ARM = "arm"
    ARM64 = "arm64"
    Other = "other"

    @classmethod
    @lru_cache(1)
    def get_arch(cls, arch_str: str = platform.machine()) -> "Arch":
        arch_str = arch_str.lower().replace("_", "")
        if arch_str == "amd64":
            return cls.x64
        if arch_str == "i386":
            return cls.x86
        if arch_str == "arm":
            return cls.ARM
        if arch_str == "arm64":
            return cls.ARM64
        return cls.Other

env_os = System.get_os()
