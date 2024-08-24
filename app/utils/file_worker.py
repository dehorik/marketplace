import os
from abc import ABC, abstractmethod

from utils.uuid_generator import IDGenerator


class IntefaceFileWorker(ABC):
    """
    Каждый класс для работы с файлами должен имплементировать метод __call__,
    в нём и реализовывать всю логику.
    """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class FileWriter(IntefaceFileWorker):
    user_path = '/database_data/user_photo'
    product_path = '/database_data/product_photo'
    comment_path = '/database_data/comment_photo'

    def __call__(self, path: str, file: bytes) -> str:
        """
        :param path: передать путь, по которому записывать файл (можно найти в атрибутах класса);
        :param file: сам файл;
        :return: вернётся путь к записанному файлу
        """

        if path not in [self.user_path, self.product_path, self.comment_path]:
            raise Exception('wrong path!')

        generator = IDGenerator()

        path = f"{path}/{generator()}"
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)

        return path


class FileReWriter(IntefaceFileWorker):
    """Класс для перезаписи файла"""

    def __call__(self, path: str, file: bytes) -> None:
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)


class FileDeleter(IntefaceFileWorker):
    """Класс для удаления файла"""

    def __call__(self, path):
        relative_path = f"../{path}"
        os.remove(relative_path)
