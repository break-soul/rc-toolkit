import hashlib
import typing
from os import path, makedirs
from pathlib import Path
from functools import partial
from ..env import is_debug
from ..enums import HashType

def mkdir(f_path: str, is_dir: bool = False) -> typing.NoReturn: # type: ignore
    """
    make file dirs

    Args:
        file_path (str): file path
    """
    f_path:Path = Path(f_path) # type: ignore
    if not is_dir:
        f_path = f_path.parent
    if path.isdir(f_path): return # type: ignore
    try: makedirs(f_path)
    except Exception:  # pylint: disable=broad-exception-caught
        if not is_debug(): return   # type: ignore
        raise

def get_name(f_path: str) -> list:
    f_path = Path(f_path)    # type: ignore
    return [f_path.stem, f_path.suffix] # type: ignore

def get_hash(file ,algorithm = HashType.BLAKE2 ,* ,chunk_size = 128*1048576, max_workers = None):
    hash_obj = hashlib.new(algorithm.value)
    with open(file , "rb") as f:

        for chunk in iter(partial(f.read ,chunk_size), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

def verify_hash(file, hash_str, algorithm = HashType.BLAKE2):
    act_hash = get_hash(file, algorithm)
    if act_hash == hash_str.lower():
        return True
    return False
