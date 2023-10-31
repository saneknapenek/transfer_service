import base64
import json
from typing import Annotated

from fastapi import Depends, APIRouter, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from celery.result import AsyncResult

from utils.yrequests.requests import AsyncClientYandex
from tasks.tasks import clr

from schemes import ListNames

from actions import (get_object_for_path, get_objects_for_page, get_link_for_download,
                     delete_object_for_name, get_all_objects, disk_initialization)

from env import CLIENT_ID, CLIENT_SECRET

from auth.security import get_current_user, get_client_session

from db.settings import get_db_session
from db.repositories.service import ServiceAlchemy
from db.models import SERVICES


yandex_auth = APIRouter(tags=["auth"])


@yandex_auth.get("/include")  #in auth
async def include_service(code: str = "",
                          current_user = Depends(get_current_user),
                          db_session: AsyncSession = Depends(get_db_session)):
    if code == "":
        return RedirectResponse(
            url=f"https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}"
        )
    else:
        async with AsyncClient() as session:
            auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
            auth_string_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            authorization_header = f"Basic {auth_string_encoded}"
            response = await session.post(
                url="https://oauth.yandex.ru/token",
                headers={
                    "Content-type": "application/x-www-form-urlencoded",
                    "Authorization": authorization_header
                },
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET
                }
            )
            data = {
                "name": SERVICES.YANDEX.value,
                "user_email": "test@test.ru",
                "user_id": current_user["id"],
                "token": response.json()["access_token"]
            }
            service_db = ServiceAlchemy(db_session)
            res = await service_db.get_for_user(name=SERVICES.YANDEX.value, user_id=current_user["id"])
            if res is None:
                await service_db.create(data=data)
            else:
                await service_db.delete(id=res.id)
                await service_db.create(data=data)
            return status.HTTP_200_OK
    
@yandex_auth.get("/exclude")  #in auth
async def exclude_service(current_user=Depends(get_current_user),
                          db_session: AsyncSession = Depends(get_db_session)):
    await ServiceAlchemy(db_session).delete_for_user(name=SERVICES.YANDEX.value,
                                                     user_id=current_user["id"])
    return status.HTTP_200_OK


server_router = APIRouter(tags=["server"])


@server_router.get("/")
async def get_object(name: str, session: Annotated[AsyncClientYandex, Depends(get_client_session)]):
    return await get_object_for_path(session=session, path=name)

@server_router.get("/download")
async def download(name: str, session: Annotated[AsyncClientYandex, Depends(get_client_session)]):
    link = await get_link_for_download(name=name, session=session)
    return Response(content=json.dumps({"link": link}),
                    status_code=status.HTTP_200_OK)

@server_router.delete("/")
async def delete_object(name: str, session: Annotated[AsyncClientYandex, Depends(get_client_session)]):
    response: dict =  await delete_object_for_name(name=name, session=session)
    return Response(status_code=response["status_code"],
                    content=response["content"])

@server_router.get("/page/{page}", response_model=list)
async def get_objects(quantity_on_page: int, page: int, session: Annotated[AsyncClientYandex, Depends(get_client_session)]):
    response = await get_objects_for_page(
        quantity_on_page, page, session
    )
    return response


service_router = APIRouter(tags=["init media"], prefix="/i")


@service_router.get("/page/{name}")
async def get_init_object(name: str):
    pass

@service_router.get("/")
async def get_init_objects(quantity_on_page: int, page: int):
    pass

@service_router.delete("/")
async def delete_init_objcets(body: ListNames):
    pass

@service_router.get("/init")
async def init_disk(session: AsyncClientYandex = Depends(get_client_session)) -> dict:
    task_id = await disk_initialization(session=session)
    return {"initialization_id": task_id}

@service_router.get("/init/{id}")
async def check_init(id: str):
    res = AsyncResult(id=id, app=clr)
    if res.ready():
        if res.successful():
            msg =  "Initialization completed successfully"
        else:
            msg =  "Initialization error"
    else:
        msg = "Initialization did not complete"
    res.forget()
    return Response(content=msg)

test_router = APIRouter(tags=["test"])


@test_router.get("/current_user")
async def test(current_user=Depends(get_current_user)):
    return current_user

@test_router.get("/all")
async def all_objects(session: Annotated[AsyncClientYandex, Depends(get_client_session)]):
    return await get_all_objects(session)
