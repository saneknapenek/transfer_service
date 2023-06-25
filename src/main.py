from fastapi import FastAPI
from fastapi import APIRouter



app = FastAPI()


mainRouter = APIRouter()
app.include_router(mainRouter)