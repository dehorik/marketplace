import os

from core.settings import ROOT_PATH


def exists(path: str) -> bool:
    # параметр path: путь к файлу относительно директории marketplace
    return os.path.exists(os.path.join(ROOT_PATH, path))

def write_file(path: str, file: bytes) -> None:
    # параметр path: путь к файлу относительно директории marketplace
    # используется и для записи, и для перезаписи файлов

    with open(os.path.join(ROOT_PATH, path), 'wb') as photo:
        photo.write(file)

def delete_file(path: str) -> None:
    # параметр path: путь к файлу относительно директории marketplace
    os.remove(os.path.join(ROOT_PATH, path))
