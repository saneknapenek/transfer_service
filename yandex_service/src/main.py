from fastapi import FastAPI

import handlers
from redis_om import Migrator



app = FastAPI()

app.include_router(handlers.server_router, prefix="/yandex")
app.include_router(handlers.yandex_auth, prefix="/yandex")
app.include_router(handlers.service_router, prefix="/yandex")

app.include_router(handlers.test_router, prefix="/yandex")

@app.on_event("startup")
async def start_event():
    Migrator().run()