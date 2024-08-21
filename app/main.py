from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.database import Session
from routes import product_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    session = Session()
    yield
    session.close_connection()


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
