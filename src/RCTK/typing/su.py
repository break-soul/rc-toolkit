import warnings
from functools import wraps
from typing import TYPE_CHECKING, TypeAlias


if TYPE_CHECKING:
    from pathlib import Path
    from ctypes import _CArgObject, _Pointer, c_int

PathLike: TypeAlias = "Path | str"

CPointInt: TypeAlias = "_Pointer[c_int] | _CArgObject"


def deprecated(func, args):
    warnings.warn(
        f"{func.__name__} is deprecated and will be removed in a future version.{args}",
        DeprecationWarning,
        stacklevel=2,
    )

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
