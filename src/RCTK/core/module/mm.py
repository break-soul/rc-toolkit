import json
from pathlib import Path
from os import path as os_path
from collections import UserDict
from typing import Union, Optional, Any

from ...tk_io import compress
from ..enums import MISSING, MISSING_TYPE


def _load_json(file: str) -> dict:
    return json.load(compress.decompress_with_zstd(f_zst=file, arcname="main")) # type: ignore


def _write_json(file: str, data: dict) -> None:
    compress.compress_with_zstd(
        f_obj=json.dumps(data).encode("utf-8"), f_name=file, arcname="main"
    )


class MM(UserDict):
    def __init__(self, file: Optional[str] = None, **kw) -> None:
        self.file = file
        super().__init__(self, **kw)
        if self.file is not None:
            if os_path.isfile(self.file):
                self.load()
            else:
                self.write()

    def load(self) -> Union[dict, int]:
        if self.file == None:
            return -1
        self.data = _load_json(self.file)
        return self.data

    def write(self) -> Optional[int]:
        if self.file == None:
            return -1
        _write_json(self.file, self.data)

    def write_back(
        self, key, value: Union[Any, MISSING_TYPE] = MISSING
    ) -> Optional[int]:
        if self.file == None:
            return -1
        if value == MISSING:
            value = self.data[key]
        self.load()
        self.data[key] = value
        self.write()

    def sync(self) -> Optional[int]:
        if self.file == None:
            return -1
        f_data = _load_json(self.file)
        f_data.update(self.data)
        self.data = f_data
        _write_json(self.file, self.data)

    def clear(self) -> dict:  # type: ignore
        data = self.data
        self.data = {}
        return data
