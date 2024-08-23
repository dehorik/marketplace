import os
from abc import ABC, abstractmethod

from utils.uuid_generator import IDGenerator


class IntefaceFile(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class FileWriter(IntefaceFile):
    user_path = '/database_data/user_photo'
    product_path = '/database_data/product_photo'
    comment_path = '/database_data/comment_photo'

    def __call__(self, path: str, file: bytes) -> str:
        generator = IDGenerator()

        path = f"{path}/{generator()}"
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)

        return path


class FileReWriter(IntefaceFile):
    def __call__(self, path: str, file: bytes):
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)


class FileDeleter(IntefaceFile):
    def __call__(self, path):
        relative_path = f"../{path}"
        os.remove(relative_path)
