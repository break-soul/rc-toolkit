from abc import ABC, abstractmethod
from atexit import register as atexit_register
from collections import deque
from collections.abc import Callable
from copy import copy
from enum import IntEnum
from fnmatch import fnmatchcase
from functools import partial, lru_cache
from pathlib import Path
from sys import stdout
from threading import Lock, Thread
from time import time, mktime, strftime, strptime, sleep
from traceback import format_exception
from typing import Any, Self

from RCTK.core.lazy_do import lazy_do


# region meta
class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class Buffer(ABC):
    @abstractmethod
    def __init__(self, level: LogLevel): ...

    @abstractmethod
    def clean(self): ...

    @abstractmethod
    def write(self, msg: Any, level: LogLevel): ...

    @abstractmethod
    def flush(self): ...


# endregion

# region inline
try:
    import cython

    @cython.inline
    def _reflush(buffer: Buffer, pool: str) -> deque[Any]:
        old_pool = getattr(buffer, pool)
        setattr(buffer, pool, deque())
        return old_pool

    @cython.inline
    def _file_bak_path(file: Path, i: int) -> Path:
        return file.with_suffix(f".{i}{file.suffix}")

except ImportError:

    def _reflush(buffer: Buffer, pool: str) -> deque[Any]:
        old_pool = getattr(buffer, pool)
        setattr(buffer, pool, deque())
        return old_pool

    def _file_bak_path(file: Path, i: int) -> Path:
        return file.with_suffix(f".{i}.{file.suffix}")


# endregion

# region buffer


class StdoutBuffer(Buffer):
    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.stdout_pool: deque[str] = deque()
        self.stderr_pool: deque[str] = deque()
        self.lock = Lock()
        self.level = level

    def clean(self): ...
    def write(self, msg, level: LogLevel):
        if level < self.level:
            return
        (self.stderr_pool if level >= LogLevel.ERROR else self.stdout_pool).append(
            str(msg)
        )

    def flush(self):
        with self.lock:
            if self.stdout_pool:
                pool = _reflush(self, "stdout_pool")
                stdout.write("\n".join(pool) + "\n")
            if self.stderr_pool:
                pool = _reflush(self, "stderr_pool")
                stdout.write("\n".join(pool) + "\n")


class FileBuffer(Buffer):

    def __init__(
        self,
        filename: str = "%Y-%m-%d_log.log",
        max_bytes: int = 1048576,
        backup_count: int = 3,
        backup_days: int = 0,  # 0 disable
        encoding: str = "utf8",
        level: LogLevel = LogLevel.INFO,
    ):
        self.filename = Path(filename)
        self.file = Path(strftime(filename))
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.pool: deque[str] = deque()
        self.lock = Lock()
        self.level = level
        self.max_bytes = max_bytes
        self.back_count = backup_count
        self.backup_days = backup_days
        self.encoding = encoding

        # delete over backup days logs
        if backup_days > 0:
            self.clean()

    def clean(self):
        now = time()
        for item in self.file.parent.iterdir():
            if item.is_file() and item.suffix == self.file.suffix:
                try:
                    f_time = mktime(
                        strptime(
                            item.name.split(".")[0], self.filename.name.split(".")[0]
                        )
                    )
                except Exception:
                    continue
                if (now - f_time) > self.backup_days * 86400:
                    print(f"Delete log file {item}!")
                    item.unlink()

    def write(self, msg, level: LogLevel):
        if level < self.level:
            return
        self.pool.append(msg)

    def flush(self):
        with self.lock:
            if self.pool:
                pool = _reflush(self, "pool")
                with self.file.open("a", encoding=self.encoding) as f:
                    f.write("\n".join(pool) + "\n")
                if self.file.stat().st_size > self.max_bytes:
                    if (p := _file_bak_path(self.file, self.back_count)).is_file():
                        p.unlink()
                    for i in range(self.back_count - 1, 0, -1):
                        if (p := _file_bak_path(self.file, i)).is_file():
                            p.rename(_file_bak_path(self.file, i + 1))
                    self.file.rename(_file_bak_path(self.file, 1))
                    self.file = Path(strftime(self.file.name))


# endregion


class Logger:

    def __init__(
        self,
        name: str,
        buffers: list[Buffer],
        level: LogLevel = LogLevel.INFO,
        fmt: str = "<{time}>[{level}]{name}:{msg}",
        timefmt: str = "%Y-%m-%d %H:%M:%S",
    ):
        self.name = name
        self.fmt = fmt
        self.level = level
        self.timefmt = timefmt
        self.buffers: list[Buffer] = buffers if buffers is not None else []

        self.debug: Callable[[Any], None] = partial(self.log, LogLevel.DEBUG)
        self.info: Callable[[Any], None] = partial(self.log, LogLevel.INFO)
        self.warning: Callable[[Any], None] = partial(self.log, LogLevel.WARNING)
        self.error: Callable[[Any], None] = partial(self.log, LogLevel.ERROR)
        self.critical: Callable[[Any], None] = partial(self.log, LogLevel.CRITICAL)

    def log(self, level: LogLevel, msg: Any):
        if self.level > level:
            return
        ts = strftime(self.timefmt)
        for buffer in self.buffers:
            buffer.write(
                self.fmt.format(name=self.name, time=ts, level=level.name, msg=msg),
                level,
            )

    def exception(self, msg, error: Exception):
        stack = format_exception(error)
        stack.append(msg)
        self.log(LogLevel.ERROR, "\n".join(stack))

    def new(self, name: str) -> Self:
        logger = copy(self)
        logger.name = name
        return logger


class LogConfig:
    def __init__(self):
        self.level = LogLevel.INFO
        self.fmt = "<{time}>[{level}]{name}:{msg}"
        self.timefmt = "%Y-%m-%d %H:%M:%S"
        self.logger_dt: dict[str, Logger] = {}
        self.buffer_dt: dict[str, Buffer] = {"Console": StdoutBuffer()}
        self.buffers_dt: dict[str, list[Buffer]] = {
            "default": [self.buffer_dt["Console"]]
        }
        self.flush_time = 0.1
        self._t = Thread(target=self._flush_loop, daemon=True)
        self._t.start()
        atexit_register(self._at_exit)

    def _at_exit(self):
        self._t.join(timeout=0.1)
        self._flush()

    def _flush(self):
        for buffer in self.buffer_dt.values():
            buffer.flush()

    def _flush_loop(self):
        while True:
            sleep(self.flush_time)
            self._flush()

    def register_buffer(self, name: str, buffer: Buffer):
        self.buffer_dt[name] = buffer

    def get_buffer(self, name: str) -> Buffer | None:
        return self.buffer_dt.get(name)

    def set_default_buffer(self, buffers: list[Buffer]):
        self.buffers_dt["default"] = buffers

    def set_logger(self, name: str, logger: Logger):
        self.logger_dt[name] = logger

    def set_default_level(self, level: LogLevel):
        self.level = level

    @lru_cache(maxsize=32768)
    def get_logger(self, name: str = "main") -> Logger:
        if logger := self.logger_dt.get(name):
            return logger
        for pattern, logger in self.logger_dt.items():
            if fnmatchcase(name, pattern):
                self.logger_dt[name] = logger
                return logger
        logger = Logger(
            name, self.buffers_dt["default"], self.level, self.fmt, self.timefmt
        )
        self.logger_dt[name] = logger
        return logger


config = LogConfig()


@lazy_do
def get_log(name: str) -> Logger:
    return config.get_logger(name)

def hook(builtin=True, print_=True):
    if builtin or print_:
        from RCTK.runtime.py_env import set_global

        if builtin:
            set_global("get_log", get_log)
        if print_:
            log_print = get_log("Print")
            def _hook_print(*objects, sep=" ", end="\n", file=None, flush=False):
                return log_print.debug((sep.join(map(str, objects)) + end).replace("\n", " "))
            set_global("print", _hook_print)
