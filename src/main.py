from fastapi import FastAPI
from fastapi import APIRouter

from user.handlers import user_router
from user.handlers import auth_router
from user.handlers import admin_router



app = FastAPI()


mainRouter = APIRouter()
app.include_router(mainRouter)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)
