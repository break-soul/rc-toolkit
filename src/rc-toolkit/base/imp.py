
from typing import Any, Tuple
from functools import lru_cache

from .enums import CompactType, EncryptType

# region compact

# region zstd


def get_error(module_name: str) -> "str":
    return ImportError(f"You need to install {module_name} to use this function")


@lru_cache(3)
def get_zstd(i: int = 0) -> "object":
    """
    0 is for compress, 1 is for decompress, other is invalid
    """
    try:
        if i == 0:
            from zstandard import ZstdCompressor as zstd  # type: ignore
        elif i == 1:
            from zstandard import ZstdDecompressor as zstd  # type: ignore
        else:
            raise ValueError("Invalid i")
    except ImportError:
        get_error("zstandard")
    return zstd


# endregion


@lru_cache(16)
def get_compact(compact_type: CompactType, i: int = 0) -> "object":
    """
    This function returns either a compressed or decompressed object based on the specified compact
    type.
    
    :param compact_type: CompactType
    :type compact_type: CompactType
    :param i: The parameter `i` is an integer that has a default value of 0. It is used as an argument
    for the `get_compact` function to specify the operation to be performed based on the `compact_type`,
    defaults to 0
    :type i: int (optional)
    :return: the result of calling the `get_zstd(i)` function if the `compact_type` is
    `CompactType.ZSTD`. If the `compact_type` is not `CompactType.ZSTD`, it raises a `ValueError` with
    the message "Invalid compact_type".
    """

    if compact_type == CompactType.ZSTD:
        return get_zstd(i)
    raise ValueError("Invalid compact_type")


# endregion

# region encrypt


# region ed25519
@lru_cache(3)
def get_ed25519() -> "object":
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519  # type: ignore
    except ImportError:
        get_error("cryptography")
    return ed25519


# endregion


def get_encrypt(encrypt_type: EncryptType) -> "Tuple[object, object]":

    if encrypt_type == EncryptType.ED25519:
        encrypt = get_ed25519()
    else:
        raise ValueError("Invalid encrypt_type")

    from cryptography.hazmat.primitives import serialization  # type: ignore

    return encrypt, serialization

# endregion
