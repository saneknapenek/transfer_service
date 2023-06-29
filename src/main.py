from fastapi import FastAPI
from fastapi import APIRouter

from user import handlers



app = FastAPI()


mainRouter = APIRouter()
app.include_router(mainRouter)
app.include_router(handlers.user_router)
