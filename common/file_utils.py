from pathlib import Path
import os


def create_test_file(path, size_mb, seed=12345):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    target = size_mb * 1024 * 1024
    block = bytearray(1024 * 1024)
    value = seed % 256
    for i in range(len(block)):
        block[i] = (value + i) % 256
    with path.open('wb') as f:
        remaining = target
        while remaining:
            n = min(len(block), remaining)
            f.write(block[:n])
            remaining -= n
    return path


def file_size(path):
    return os.path.getsize(path)
