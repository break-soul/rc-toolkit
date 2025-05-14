
import os
import tarfile
from io import BytesIO

# region magic
MAGIC_NUMBER = b"RCCP"   # 4bit magic/
VERSION = b"\x01"   # 1bit version
HEADER_SIZE = 8 # 3bit save
# endregion

def compress_with_zstd(flist, filename):
    for path in flist:  # check path is true
        if not os.path.exists(path):
            raise FileNotFoundError(f"Can't find '{path}'")
    
    from zstandard import ZstdCompressor
    cctx = ZstdCompressor()        # create zstd compress

    with open(filename, 'wb') as dest_file:
        # region write magic numble
        dest_file.write(MAGIC_NUMBER)   # 4bit magic
        dest_file.write(VERSION)    # 1bit version
        dest_file.write(b'\x00'*3)  # 3bit save
        # endregion
        with cctx.stream_writer(dest_file) as compressed_stream:    # create compress stream
            with tarfile.open(mode='w|', fileobj=compressed_stream) as tar: # create tar stream
                for path in flist:
                    arcname = os.path.basename(path)    # get basename to arcname
                    tar.add(path, arcname=arcname, recursive=True)

def decompress_zstd(zst_file, extract_path='.'):
    buffer = BytesIO()  # create buff cache
    
    with open(zst_file, 'rb') as f:
        # region cheak magec numble
        header = f.read(HEADER_SIZE)
        if len(header) < HEADER_SIZE:
            raise ValueError("Magic Numble Error")
            
        magic = header[:4]
        version = header[4]
        
        if magic != MAGIC_NUMBER:
            raise ValueError("Not Support File Type")
        if version != ord(VERSION):
            raise ValueError("Not Support Version")
        # endregion
        
        from zstandard import ZstdDecompressor 
        dctx = ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            while True:
                chunk = reader.read(1024*1024)  # 1MB chunks
                if not chunk:break
                buffer.write(chunk)
    
    buffer.seek(0)   # rebuff and and dump
    with tarfile.open(fileobj=buffer, mode='r:') as tar:
        members = [m for m in tar 
                  if m.isfile() and not m.name.startswith(('/', '\\'))] # filter
        tar.extractall(extract_path, members=members)
