from utils.uuid_generator import IDGenerator


class FileWriter:
    """
    Класс для записи фотографий из БД на диск.
    В самой БД лежит лишь путь к нужному файлу.
    """

    product = "database_data/product_photo"
    user = "database_data/user_photo"
    comment = "database_data/comment_photo"

    def __init__(self, path):
        if path not in [self.photo, self.user, self.comment]:
            raise Exception('unavailable path!')

        self.__path = path

    def __call__(self, file) -> str:
        generator = IDGenerator()

        path = f"{self.__path}/{generator()}"
        relative_path = f"../{path}"

        with open(relative_path, 'wb') as photo:
            photo.write(file)

        return path
