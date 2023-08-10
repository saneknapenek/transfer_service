from fastapi import FastAPI, Depends, status
from fastapi.responses import RedirectResponse
from httpx import AsyncClient
from pydantic import BaseModel
from environs import Env
from urllib.parse import urlencode

from env import AUTH_URI, CLIENT_ID, REDIRECT_URI_CALLBACK, REDIRECT_URI_TOKEN, TOKEN_URI, CLIENT_SECRET

app = FastAPI()


TOKEN = ...
async def get_client_session() -> AsyncClient:
    if TOKEN is None:
        raise 
    client = AsyncClient(headers={"Authorization": f"OAuth {TOKEN}"})
    try:
        yield client
    finally:
        await client.aclose()


@app.get("/include", response_class=RedirectResponse)
async def include_google():
    url = f"{AUTH_URI}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI_CALLBACK}&scope=https://www.googleapis.com/auth/photoslibrary&response_type=code&access_type=offline"
    return url


@app.get("/callback")
async def auth(code: str, scope: str):
    print(code)
    async with AsyncClient() as session:
        response = await session.post(
            url=TOKEN_URI,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=urlencode({
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI_TOKEN,
                'grant_type': 'authorization_code'
            })
        )
        # if response.status_code == 200:
        #     token_data = response.json()
        #     access_token = token_data['access_token']
        #     refresh_token = token_data['refresh_token']
        #     expires_in = token_data['expires_in']
        #     print({
        #         "access_token": token_data['access_token'],
        #         "refresh_token": token_data['refresh_token'],
        #         "expires_in": token_data['expires_in']
        #     })
        # else:
        #     print('Ошибка при получении токена доступа:', response.text)
        return response.status_code