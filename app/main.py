from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.database.session_factory import BaseSession, ConnectorData
from core.config_reader import config
from routes.products_router import router as product_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    Тут создаётся ссесия для работы с БД. Вообще, по идее,
    за всё время работы программы объект BaseSession будет всего один,
    на него просто будет множество ссылок: такое поведение обеспечивает
    паттерн Singleton.

    В конце работы программы сессия автоматически закроется, как только с переменной
    session из этой функции пропадут все ссылки (т.е мы дойдем до конца этой функции).
    Однако в конце явно прописано "del session" для большей наглядности,
    всё-таки явное лучше неявного=)
    """

    connection_data = ConnectorData(config)
    session = BaseSession(connection_data)
    yield
    del session


app = FastAPI(
    lifespan=lifespan,
    title='marketplace'
)

app.include_router(product_router)


@app.get('/')
def root():
    return {
        'message': 'hello world!'
    }
