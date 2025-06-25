
from functools import wraps
from typing import Callable, Union, Any

def lazy_do(func: Callable) -> Callable:
    @wraps(func)
    def warpper(*args, **kw):
        return func(*args, **kw)
    
    return warpper