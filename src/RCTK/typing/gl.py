
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

def get_log() -> "Logger": ...

def lazy_import() -> object: ...
