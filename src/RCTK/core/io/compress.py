
import os
import tarfile
from io import BytesIO
from functools import lru_cache

from ..error import imp_error

# region import
@lru_cache(3)
def get_zstd(i: int = 0) -> "object":
    """
    0 is for compress, 1 is for decompress, other is invalid
    """
    try:
        if i == 0:
            from zstandard import ZstdCompressor as zstd  # type: ignore
        elif i == 1:
            from zstandard import ZstdDecompressor as zstd  # type: ignore
        else:
            raise ValueError("Invalid i")
    except ImportError:
        imp_error("zstandard")
    return zstd
# endregion

# region magic
MAGIC_NUMBER = b"RCCP"   # 4bit magic/
VERSION = b"\x01"   # 1bit version
HEADER_SIZE = 8 # 3bit save
# endregion

def compress_with_zstd(file_list, filename):
    for path in file_list:  # check path is true
        if not os.path.exists(path):
            raise FileNotFoundError(f"Can't find '{path}'")
    
    cctx = get_zstd(0)        # create zstd compress

    with open(filename, 'wb') as dest_file:
        # region write magic
        dest_file.write(MAGIC_NUMBER)   # 4bit magic
        dest_file.write(VERSION)    # 1bit version
        dest_file.write(b'\x00'*3)  # 3bit save
        # endregion
        with cctx.stream_writer(dest_file) as compressed_stream:    # create compress stream
            with tarfile.open(mode='w|', fileobj=compressed_stream) as tar: # create tar stream
                for path in file_list:
                    arcname = os.path.basename(path)    # get basename to arcname
                    tar.add(path, arcname=arcname, recursive=True)

def decompress_zstd(zst_file, extract_path='.'):
    buffer = BytesIO()  # create buff cache
    
    with open(zst_file, 'rb') as f:
        # region check magic 
        header = f.read(HEADER_SIZE)
        if len(header) < HEADER_SIZE:
            raise ValueError("Magic Error")
            
        magic = header[:4]
        version = header[4]
        
        if magic != MAGIC_NUMBER:
            raise ValueError("Not Support File Type")
        if version != ord(VERSION):
            raise ValueError("Not Support Version")
        # endregion
        
        dctx =get_zstd(1)
        with dctx.stream_reader(f) as reader:
            while True:
                chunk = reader.read(1024*1024)  # 1MB chunks
                if not chunk:break
                buffer.write(chunk)
    
    buffer.seek(0)   # rebuff and and dump
    with tarfile.open(fileobj=buffer, mode='r:') as tar:
        members = [m for m in tar if m.isfile() and not m.name.startswith(('/', '\\'))]
        tar.extractall(extract_path, members=members)
