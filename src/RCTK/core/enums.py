"""
Store the enums used in the package.
"""

from enum import Enum


def mode_func(*args, **kw): ...


class MISSING_TYPE:
    pass


MISSING = MISSING_TYPE()


class DataType(Enum):
    File = b"0000"
    Object = b"0001"
    Text = b"0010"
    JSON = b"0011"
    Dict = b"0100"


class CompactType(Enum):
    ZIP = b"0000"
    TAR = b"0001"
    GZTAR = b"0010"
    BZTAR = b"0011"
    XZTAR = b"0100"
    ZSTD = b"0101"


class EncryptType(Enum):
    RSA_2048 = b"0000"
    ED25519 = b"0001"
    ECDSA = b"0010"


class HashType(Enum):
    SHA_256 = "sha256"
    SHA_384 = "sha384"
    SHA_512 = "sha512"
    BLAKE2 = "blake2b"


class Release(Enum):
    ALPHA = "a"
    BETA = "b"
    RELEASE = "r"
    DEBUG = "d"

    @classmethod
    def from_str(cls, rel_str: str) -> "Release":
        if rel_str == "a":
            return cls.ALPHA
        if rel_str == "b":
            return cls.BETA
        if rel_str == "r":
            return cls.RELEASE
        if rel_str == "d":
            return cls.DEBUG
        raise ValueError("Invalid release string")


class MAGIC(Enum):
    MAGIC_NUMBER = b"MGNB"  # 4bit magic/
    VERSION = b"\x01"  # 1bit version
    HEADER_SIZE = 8  # 3bit save


class RCCP_MAGIC(Enum):
    MAGIC_NUMBER = b"RCCP"  # 4bit magic/
    VERSION = b"\x01"  # 1bit version
    HEADER_SIZE = 8  # 3bit save
