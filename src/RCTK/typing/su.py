import warnings
from pathlib import Path
from functools import wraps
from typing import TypeAlias


PathLike: TypeAlias = Path | str


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
