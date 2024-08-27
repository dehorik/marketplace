class Singleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls is Singleton:
            raise Exception('the singleton class can not have any objects')

        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance
