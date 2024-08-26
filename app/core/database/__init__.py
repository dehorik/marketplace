from core.database.session_factory import Session, ConnectionData

from core.database.crud_product import ProductDataBase
from core.database.crud_user import UserDataBase
from core.database.crud_comment import CommentDataBase


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
# Сессия закроется автоматически, как только с объекта сессии пропадут все ссылки (__del__).
