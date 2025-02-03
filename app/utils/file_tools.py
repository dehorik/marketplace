from os import remove
from os.path import exists, join

from core.settings import ROOT_PATH


class FileWriter:
    def __init__(self, base_path: str, file_format: str = "jpg"):
        self.__base_path = base_path
        self.__file_format = file_format

    def __call__(self, item_id: str | int, file: bytes) -> str:
        path = join(ROOT_PATH, self.__base_path, f"{item_id}.{self.__file_format}")

        with open(path, "wb") as photo:
            photo.write(file)

        return path


class FileRemover:
    def __init__(self, base_path: str, file_format: str = ".jpg"):
        self.__base_path = base_path
        self.__file_format = file_format

    def __call__(self, item_id: str | int) -> str | None:
        path = join(ROOT_PATH, self.__base_path, f"{item_id}{self.__file_format}")

        if exists(path):
            remove(path)
            return path
        else:
            return None
