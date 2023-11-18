import json

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from user.handlers import user_router
from user.handlers import auth_router
from user.handlers import admin_router
from user.exceptions import UserAlreadyExists



app = FastAPI()


mainRouter = APIRouter()
app.include_router(mainRouter)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.exception_handler(RequestValidationError)
async def validation_exc_handler(request, exc):
    error_message = {
        "detail":  {
            "loc": exc.errors()[0]["loc"],
            "msg": exc.errors()[0]["msg"]
        },
    }
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_message)

@app.exception_handler(IntegrityError)
async def db_duplicate_exc_handler(request, exc: IntegrityError):
    if "UniqueViolationError" in str(exc._message):
        error_message = {
            "detail": {
                "msg": "A user with the same username or email already exists"
            }
        }
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=error_message)
    return exc.orig