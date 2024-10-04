import os

from core.settings import config


class PathGenerator:
    def __init__(self, path: str):
        if path not in [
                config.USER_PHOTO_PATH,
                config.PRODUCT_PHOTO_PATH,
                config.COMMENT_PHOTO_PATH
        ]:
            raise ValueError("unavailable path")

        self.__path = path

    def __call__(self, identifier: int) -> str:
        return f"{self.__path}/{identifier}"


class FileWriter:
    def __call__(self, path: str, file: bytes) -> None:
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)


class FileRewriter:
    def __call__(self, path: str, file: bytes) -> None:
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)


class FileDeleter:
    def __call__(self, path: str) -> None:
        relative_path = f"../{path}"
        os.remove(relative_path)
