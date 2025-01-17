from typing import TYPE_CHECKING

from ..enums import MISSING, Version, CompactType, EncryptType

if TYPE_CHECKING:
    from io import TextIOWrapper


class MicroCode(object):

    def __init__(self, **kw):
        self.set_base_code(**kw)

    def set_base_code(
        self,
        identifier: bytes = b"0000",
        is_compact: bool = False,
        is_encrypt: bool = False,
        prime: bytes = b"000",
        is_hash: bool = False,
        expand_len: int = 0,
        **kw,
    ):
        self.identifier = identifier
        self.is_compact = is_compact
        self.is_encrypt = is_encrypt
        self.prime = prime
        self.is_hash = is_hash
        if expand_len < 0:
            raise ValueError("expand_len must be greater than or equal to 0")
        if is_compact or is_encrypt and expand_len == 0:
            raise ValueError(
                "expand_len must be greater than 0 when is_compact is True or is_encrypt is True"
            )
        if expand_len > 63:
            raise IndexError("expand_len must be less than or equal to 63")
        self.expand_len = expand_len
        self._mc = b"".join(
            [
                self.identifier,
                b"1" if self.is_compact else b"0",
                b"1" if self.is_encrypt else b"0",
                self.prime,
                b"1" if self.is_hash else b"0",
                bin(self.expand_len).replace("0b", "").rjust(4, "0").encode(),
            ]
        )

    def set_first_block(
        self,
        version: Version,
        compact_type: CompactType = MISSING,
        encrypt_type: EncryptType = MISSING,
        **kw,
    ): ...

    @classmethod
    def load_mc(cls, fp: "TextIOWrapper") -> "MicroCode": ...

    def dump_mc(self, fp: "TextIOWrapper") -> None: ...

    def set_block(self, block_num: int, block: bytes) -> None: ...
