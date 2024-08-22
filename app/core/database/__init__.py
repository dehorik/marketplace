from core.database.session_factory import *
from core.database.crud_product import *
from core.database.crud_user import *
from core.database.crud_comment import *


# Инструкция для работы со всем этим добром, если я когда-нибудь всё же решусь
# отрефакторить тут всё:
#
# 1. Создаём экземпляр Session;
# 2. Этот объект прокидываем в инициализатор конкретного класса
#    для работы с БД (например, ProductDataBase), получаем объект;
# 3. Работаем;
# 4. В конце работы не забываем вызвать close() у объекта БД,
#    созданного на шаге 2.
#
# Сессия закроется автоматически, как только с объекта сессии пропадут все ссылки.
