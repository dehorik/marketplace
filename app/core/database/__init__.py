from core.database.session_factory import Session, ConnectionData

from core.database.crud_product import ProductDataBase
from core.database.crud_user import UserDataBase
from core.database.crud_comment import CommentDataBase
from core.database.crud_order import OrderDataBase

# 1) Создаём объект Session
# 2) С помощью созданного объекта создаём экземпляр БД
#    (ProductDataBase и подобных...)
# 3) В конце работы закрываем сессию и сам объект БД
#
# можно создавать объект БД с помощью контекстного менеджера,
# тогда изменения автоматически внесутся, а БД сама закроется
# в конце работы
