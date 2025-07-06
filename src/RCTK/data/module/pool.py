

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Callable, Sequence, Optional
from collections import deque

@dataclass
class Call:
    data: Any
    loader: List[str]
    level: int

class Pool:
    def __init__(self, downer: Optional[Callable], upper: Optional[Callable], max_size: int) -> None:
        self.downer = downer
        self.upper = upper
        self.stack: Sequence[Call] = deque(maxlen = max_size)

    def new_call(self) -> Call:
        ...
