from pickletools import bytes1
import tarfile
from os import path as os_path
from io import BytesIO, BufferedReader
from typing import Union, Optional, overload, IO

from zstandard import ZstdCompressor, ZstdDecompressor

from ..core.enums import RCCP_MAGIC
from .file import write_magic, verify_magic


def compress_with_zstd(
    f_obj: Union[list, bytes], f_name: str, *, arcname: Optional[str] = None
) -> int:
    cctx = ZstdCompressor()  # create zstd compress

    with open(f_name, "wb") as f_opt:
        write_magic(RCCP_MAGIC, f_opt)  # type: ignore
        with cctx.stream_writer(f_opt) as compressed_stream:
            with tarfile.open(
                mode="w|", fileobj=compressed_stream
            ) as tar:  # create tar stream
                if isinstance(f_obj, list):
                    for f_path in f_obj:
                        if not os_path.exists(f_path):
                            return -2
                    for f_path in f_obj:
                        tar.add(
                            f_path, arcname=os_path.basename(f_path), recursive=True
                        )
                elif isinstance(f_obj, bytes):
                    t_info = tarfile.TarInfo(
                        name="main" if arcname == None else arcname
                    )
                    t_info.size = len(f_obj)
                    tar.addfile(t_info, BytesIO(f_obj))
                else:
                    return -1
    return 0


@overload
def decompress_with_zstd(f_zst: str, *, dump: str) -> int: ...
@overload
def decompress_with_zstd(
    f_zst: str, *, arcname: str = "main"
) -> Union[int, IO[bytes]]: ...
def decompress_with_zstd(
    f_zst: str,
    *,
    dump: Optional[str] = None,
    arcname: Optional[str] = None,
    chunk_size: int = 1024 * 1024,
) -> Union[int, IO[bytes]]:
    buffer = BytesIO()

    with open(f_zst, "rb") as f_obj:
        if verify_magic(RCCP_MAGIC, f_obj) != 0:  # type: ignore
            return -1
        dctx = ZstdDecompressor()
        with dctx.stream_reader(f_obj) as reader:
            while True:
                if not (chunk := reader.read(chunk_size)):
                    break
                buffer.write(chunk)

    buffer.seek(0)  # rebuff and and dump
    with tarfile.open(fileobj=buffer, mode="r:") as tar:
        if dump != None:
            tar.extractall(
                dump,
                members=[
                    m for m in tar if m.isfile() and not m.name.startswith(("/", "\\"))
                ],
            )
            return 0
        elif arcname != None:
            return x if (x := tar.extractfile(member=arcname)) else -2
        return -1


def compress_zstd(f_byte, filename, arcname: str = "main"):
    compress_with_zstd(f_byte, filename, arcname=arcname)


def decompress_zstd(filename, arcname: str = "main"):
    return decompress_with_zstd(filename, arcname=arcname)
