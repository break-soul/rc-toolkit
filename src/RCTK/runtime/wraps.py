from functools import wraps
from typing import Callable

class LazyCallable:
    def __init__(self, func) -> None:
        setattr(self, "__func", func)
        
    
    def __getattribute__(self, __name: str):
        func = getattr(self, "__func")
        self = func
        return getattr(func, __name)
    
    def __call__(self, *args, **kw):
        func = getattr(self, "__func")
        self = func(*args, **kw)
        return self

def lazy_do(func: Callable) -> Callable:
    @wraps(func)
    def warpper(*args, **kw):
        return func(*args, **kw)
    return warpper
