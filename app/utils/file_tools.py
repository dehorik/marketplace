import os


def write_file(path: str, file: bytes) -> None:
    # используется и для записи, и для перезаписи файлов

    relative_path = f"../{path}"

    with open(relative_path, 'wb') as photo:
        photo.write(file)

def delete_file(path: str) -> None:
    relative_path = f"../{path}"
    os.remove(relative_path)
