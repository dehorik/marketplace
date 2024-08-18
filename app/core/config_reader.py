from dotenv import load_dotenv
import os


class Settings:
    """
    Класс для работы с переменными конфигурации. Требуется создать объект Settings
    с аргументом path - путь к файлу .env относительно текущего каталога.
    Получаем переменные с помощью метода getenv, передавая в него имя переменной.
    """

    def __init__(self, path: str):
        self.__dotenv_path = os.path.join(os.path.dirname(__file__), path)

        if not os.path.exists(self.__dotenv_path):
            raise Exception('incorrect path to .env file!')

        load_dotenv(self.__dotenv_path)

    @staticmethod
    def getenv(var):
        value = os.getenv(var)
        if not value:
            raise Exception("incorrect variable!")

        return value


config = Settings('../../.env')
