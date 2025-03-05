from os import remove
from os.path import exists, join

from core.settings import ROOT_PATH


class FileWriter:
    """Запись файлов"""

    def __init__(self, base_path: str, file_format: str = "jpg"):
        """
        :param base_path: путь, по которому будут писаться файлы (относительно marketplace)
        :param file_format: формат записываемых файлов
        """

        self.__base_path = base_path
        self.__file_format = file_format

    def __call__(self, item_id: str | int, file: bytes) -> str:
        """
        :param item_id: id элемента, которому принадлежит файл
        :param file: файл
        :return: путь к записанному файлу
        """

        path = join(ROOT_PATH, self.__base_path, f"{item_id}.{self.__file_format}")

        with open(path, "wb") as photo:
            photo.write(file)

        return path


class FileRemover:
    """Удаление файлов"""

    def __init__(self, base_path: str, file_format: str = "jpg"):
        """
        :param base_path: путь к директории с удаляемыми файлами (относительно marketplace)
        :param file_format: формат удаляемых файлов
        """

        self.__base_path = base_path
        self.__file_format = file_format

    def __call__(self, item_id: str | int) -> str | None:
        """
        :param item_id: id элемента, которому принадлежит файл
        :return: путь к удаленному файлу (None, если файл не был найден)
        """

        path = join(ROOT_PATH, self.__base_path, f"{item_id}.{self.__file_format}")

        if exists(path):
            remove(path)
            return path
        else:
            return None
