from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse

from core.database import Session
from routes import product_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    session = Session()
    yield
    session.close_connection()


app = FastAPI(
    lifespan=lifespan,
    title='marketplace',
)

app.include_router(product_router)


@app.get('/', response_class=FileResponse)
def root():
    return "../frontend/templates/catalog.html"

