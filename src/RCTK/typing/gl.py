
import typing

from ..core.enums import _MISSING_TYPE as MISSING_TYPE

if typing.TYPE_CHECKING:
    from logging import Logger
    

    
def get_log(logger_name: typing.Optional[str] = None) -> "Logger":
    """
    Get the logging object

    Args:
        logger_name (str): If no name is specified, return the root logger.

    Returns:
        Logger: logging object
    """
    ...

