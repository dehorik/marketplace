from jinja2 import Environment, FileSystemLoader


class TemplateEngine:
    """
    Простая оболочка над jinja.
    Передаёшь в инициализатор имя файла, путь (по умолчанию уже указан),
    вызываешь созданный объект с набором именованных параметров.
    """

    def __init__(self, template: str, path: str = '../../../frontend/templates'):
        file_loader = FileSystemLoader(path)
        env = Environment(loader=file_loader)

        self.__template = env.get_template(template)

    def __call__(self, **kwargs) -> str:
        template = self.__template.render(**kwargs)
        return template

