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

def copy_file(path_from: str, path_to: str) -> None:
    # path_from: путь к копируемому файлу
    # path_to: путь к новому файлу

    with open(os.path.join(ROOT_PATH, path_to), 'wb') as new_file:
        with open(os.path.join(ROOT_PATH, path_from), 'rb') as copied_file:
            new_file.write(copied_file.read())

def delete_file(path: str) -> None:
    # параметр path: путь к файлу относительно директории marketplace
    os.remove(os.path.join(ROOT_PATH, path))
