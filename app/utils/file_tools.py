import os
from uuid import uuid4
from abc import ABC, abstractmethod

from core.config_reader import config


class FileNameGenerator:
    def __init__(self):
        self.__file_name = uuid4()

    def __str__(self):
        return str(self.__file_name)

    @property
    def file_name(self) -> str:
        return str(self.__file_name)


class InterfaceFileWorker(ABC):
    @abstractmethod
    def __str__(self):
        # return path to file
        pass

    @property
    @abstractmethod
    def path(self):
        # return path to file
        pass


class FileWriter(InterfaceFileWorker):
    def __init__(self, path: str, file: bytes):
        if path not in [
            config.getenv('USER_PHOTO_PATH'),
            config.getenv("PRODUCT_PHOTO_PATH"),
            config.getenv("COMMENT_PHOTO_PATH")
        ]:
            raise ValueError('invalid path!')

        file_name = str(FileNameGenerator())
        self.__path = f"{path}/{file_name}"
        relative_path = f"../{self.__path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)

    def __str__(self):
        return self.__path

    @property
    def path(self) -> str:
        return self.__path


class FileReWriter:
    def __init__(self, path: str, file: bytes):
        self.__path = path
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)

    def __str__(self):
        return self.__path

    @property
    def path(self) -> str:
        return self.__path


class FileDeleter:
    def __init__(self, path: str):
        self.__path = path

        relative_path = f"../{path}"
        os.remove(relative_path)

    def __str__(self):
        return self.__path

    @property
    def path(self) -> str:
        return self.__path
