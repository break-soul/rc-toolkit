import tarfile, os, sys
from pathlib import Path
from io import BytesIO
from typing import overload, IO
from collections.abc import Callable

if sys.version_info >= (3, 14):
    from compression.zstd import ZstdFile
else:
    from backports.zstd import ZstdFile

from ..core.enums import RCCP_MAGIC
from .file import verify_magic, mkdir

from ..typing.su import PathLike


filt_t = Callable[[PathLike], bool] | None


@overload
def compress_with_zstd(
    f_obj: list[PathLike] | dict[str, PathLike | bytes], f_name: PathLike, **kw
) -> int: ...
@overload
def compress_with_zstd(
    f_obj: bytes, f_name: PathLike, *, arcname: str | None = "main", **kw
) -> int: ...
def compress_with_zstd(
    f_obj: list[PathLike] | dict[str, PathLike | bytes] | bytes,
    f_name: PathLike,
    *,
    arcname: str | None = None,
    filt: filt_t = None,
    ebackend: Callable | None = None,
    **kw,
) -> int:
    dt: dict[str, Path | bytes] = {}
    if isinstance(f_obj, list):
        f_obj = {f_path.name: f_path for f_path in map(Path, f_obj)}
    if isinstance(f_obj, dict):
        for arc_path, arc_obj in f_obj.items():
            if isinstance(arc_obj, (bytes, bytearray, memoryview)):
                dt[arc_path] = arc_obj
                continue
            if not isinstance(arc_obj, Path):
                arc_obj = Path(arc_obj)
            if not arc_obj.exists():
                raise FileNotFoundError("Can't find file {p}".format(p=arc_obj))
            g = filter(lambda x: x.is_file(), arc_obj.glob("**/*"))
            if filt != None:
                g = filter(filt, g)
            dt |= {
                os.path.join(arc_path, f_path.relative_to(arc_obj)): f_path
                for f_path in g
            }
    elif isinstance(f_obj, bytes):
        dt["main" if arcname == None else arcname] = f_obj
    else:
        return -1
    if ebackend != None:
        dt = ebackend(dt)
    with Path(f_name).open("wb") as f_opt:
        f_opt.write(
            (mg := (RCCP_MAGIC.MAGIC_NUMBER.value + RCCP_MAGIC.VERSION.value))
            + b"\x00" * (RCCP_MAGIC.HEADER_SIZE.value - len(mg))
        )
        with ZstdFile(f_opt, mode="w") as stream:
            with tarfile.open(mode="w|", fileobj=stream) as tar:
                for arc, obj in dt.items():
                    if isinstance(obj, Path):
                        print("Adding:", str(obj))
                        tar.add(obj, arcname=arc, recursive=False)
                    elif isinstance(obj, bytes):
                        t_info = tarfile.TarInfo(name=arc)
                        t_info.size = len(obj)
                        tar.addfile(t_info, BytesIO(obj))
    return 0


@overload
def decompress_with_zstd(f_zst: str, *, dump: str | Path) -> int: ...
@overload
def decompress_with_zstd(f_zst: str, *, arcname: str = "main") -> int | IO[bytes]: ...
def decompress_with_zstd(
    f_zst: str,
    *,
    dump: str | Path | None = None,
    arcname: str | None = None,
    chunk_size: int = 1024 * 1024,
) -> int | IO[bytes]:
    buffer = BytesIO()
    with open(f_zst, "rb") as f_obj:
        if verify_magic(RCCP_MAGIC, f_obj) != 0:  # type: ignore
            return -1
        with ZstdFile(f_obj, mode="r") as reader:
            while True:
                chunk = reader.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)

    buffer.seek(0)  # rebuff and and dump
    with tarfile.open(fileobj=buffer, mode="r:") as tar:
        if dump != None:
            mkdir(dump)
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


def compress_zstd(f_byte, filename, arcname: str = "main") -> int:
    return compress_with_zstd(f_byte, filename, arcname=arcname)


def decompress_zstd(filename, arcname: str = "main") -> int | IO[bytes]:
    return decompress_with_zstd(filename, arcname=arcname)
