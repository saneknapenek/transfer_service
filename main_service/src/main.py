from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from user.handlers import user_router
from user.handlers import auth_router
from user.handlers import admin_router



app = FastAPI()


mainRouter = APIRouter()
app.include_router(mainRouter)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_message = {
        "detail": [
            {
                "loc": exc.errors()[0]["loc"],
                "msg": exc.errors()[0]["msg"]
            },

        ]
    }
    return JSONResponse(status_code=422, content=error_message)