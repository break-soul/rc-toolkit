from ...runtime.lazy_import import enable_lazy_import

enable_lazy_import(global_=globals())

import json
from pathlib import Path
from collections import UserDict
from typing import IO, Any

from ...io_ import compress
from ...core.enums import MISSING, MISSING_TYPE


def _load_json(file: Path) -> dict:
    buffer = compress.decompress_with_zstd(f_zst=file, arc_name="main")
    if isinstance(buffer, int):  # decompress failed
        raise ValueError(f"Failed to decompress {file} with error code {buffer}")
    return json.load(fp=buffer)


def _write_json(file: Path, data: dict) -> None:
    compress.compress_with_zstd(
        f_obj=json.dumps(obj=data).encode(encoding="utf-8"),
        f_name=str(object=file),
        arc_name="main",
    )


class MM(UserDict):
    def __init__(self, file: str | Path | None = None, **kw) -> None:
        super().__init__(self, **kw)
        self.file: Path | None = file if file is None else Path(file)
        if self.file:
            self.load() if self.file.is_file() else self.write()

    def load(self) -> dict | int:
        if not self.file:
            return -1
        self.data = _load_json(file=self.file)
        return self.data

    def write(self) -> int | None:
        if not self.file:
            return -1
        _write_json(file=self.file, data=self.data)

    def write_back(self, key, value: Any | MISSING_TYPE = MISSING) -> int | None:
        if not self.file:
            return -1
        if value == MISSING:
            value = self.data[key]
        self.load()
        self.data[key] = value
        self.write()

    def sync(self) -> int | None:
        if not self.file:
            return -1
        f_data: dict[str, Any] = _load_json(file=self.file)
        f_data.update(self.data)
        self.data = f_data
        _write_json(file=self.file, data=self.data)

    def clear(self) -> dict:  # type: ignore
        data: dict[str, Any] = self.data
        self.data = {}
        return data
