from dataclasses import dataclass
from typing import Any
from collections import deque
from collections.abc import Callable, Sequence


@dataclass
class Cell:
    data: Any
    loader: list[str]
    level: int


class Pool:
    def __init__(
        self, downer: Callable | None, upper: Callable | None, max_size: int
    ) -> None:
        self.downer = downer
        self.upper = upper
        self.stack: Sequence[Cell] = deque(maxlen=max_size)

    def new_call(self) -> Cell: ...
