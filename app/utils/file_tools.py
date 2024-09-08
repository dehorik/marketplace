import os
from uuid import uuid4

from core.settings import config


def generate_file_name() -> str:
    return str(uuid4())

def write_file(path: str, file: bytes) -> str:
    if path not in [
        config.USER_PHOTO_PATH,
        config.PRODUCT_PHOTO_PATH,
        config.COMMENT_PHOTO_PATH
    ]:
        raise FileNotFoundError('invalid path!')

    path = f"{path}/{generate_file_name()}"
    relative_path = f"../{path}"

    with open(relative_path, 'wb') as photo:
        photo.write(file)

    return path

def rewrite_file(path: str, file: bytes) -> None:
    relative_path = f"../{path}"

    with open(relative_path, 'wb') as photo:
        photo.write(file)


def delete_file(path: str) -> None:
    relative_path = f"../{path}"
    os.remove(relative_path)
