from typing import Annotated

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from db.settings import get_db_session
from db.repositories.service import ServiceAlchemy
from db.models import SERVICES
from utils.yrequests.requests import AsyncClientYandex
from env import (HOST, MAIN_HOST, MAIN_PORT, YANDEX_PORT)



oauth2_scheme_accsess = OAuth2PasswordBearer(tokenUrl=f"http://{MAIN_HOST}:{MAIN_PORT}/authentication")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme_accsess)],
                           session: Annotated[AsyncSession, Depends(get_db_session)]) -> dict:
    
    async with AsyncClient(headers={"Authorization": f"Bearer {token}"}) as client:
        response = await client.post(url=f"http://{MAIN_HOST}:{MAIN_PORT}/currentuser")
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code,
                                headers=response.headers,
                                detail=response.json()["detail"])
        user = response.json()
        service = await ServiceAlchemy(session).get_for_user(name=SERVICES.YANDEX.value, user_id=user["id"])
        if service is None:
            return RedirectResponse(f"http://{HOST}:{YANDEX_PORT}/yandex/include")
        user["service"] = service
        return user


async def get_client_session(current_user=Depends(get_current_user)) -> AsyncClientYandex:
    client = AsyncClientYandex(headers={"Authorization": f"OAuth {current_user['service'].token}"},
                               base_url="https://cloud-api.yandex.net/v1/disk/resources",
                               root_directory="Фотокамера",
                               user=current_user)
    try:
        yield client
    finally:
        await client.aclose()
