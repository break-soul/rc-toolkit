
import os
import json
import typing
from collections import UserDict

from ..io import compress
from ..enums import MISSING

if typing.TYPE_CHECKING:
    from ...typing import *

class MM(UserDict):
    def __init__(self, file: typing.Optional[str] = None, **kw) -> None:
        self.file = file
        super().__init__(self, **kw)
        if self.file != None:
            if os.path.isfile(self.file):self.load()
            else: self.write()

    def _load(self) -> dict:
        return json.load(compress.decompress_zstd(self.file)) # type: ignore

    def load(self) -> typing.Union[dict, int]:
        if self.file == None: return -1
        self.data = self._load()
        return self.data

    def write(self) -> typing.Optional[int]:
        if self.file == None: return -1
        compress.compress_zstd(json.dumps(self.data).encode("utf-8"), self.file)

    def write_back(self, key, value:typing.Union[typing.Any, MISSING_TYPE] = MISSING) -> typing.Optional[int]:
        if self.file == None: return -1
        if value == MISSING:
            value = self.data[key]
        self.load()
        self.data[key] = value
        self.write()

    def sync(self) -> typing.Optional[int]:
        f_data = self._load()
        f_data.update(self.data)
        self.data = f_data
        self.write()
