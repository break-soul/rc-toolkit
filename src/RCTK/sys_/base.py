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
    @lru_cache(3)
    def get_os(cls, os_str: str = platform.system()) -> "System":
        return {
            "Windows": cls.Win32,
            "Linux": cls.Linux,
            "Darwin": cls.macOS,
            "Aix": cls.AIX,
            "Freebsd": cls.FreeBSD,
        }.get(os_str, cls.Other)


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
        return {
            "amd64": cls.x64,
            "i386": cls.x86,
            "arm": cls.ARM,
            "arm64": cls.ARM64,
        }.get(arch_str, cls.Other)


env_os = System.get_os()
