from contextlib import asynccontextmanager
from fastapi import FastAPI

from core import database


app = FastAPI()


@asynccontextmanager
async def lifespan(application: FastAPI):
    session = database.BaseSession()
    yield
    session.close_connection()


@app.get('/')
def root():
    return {
        'message': 'hello world!'
    }
