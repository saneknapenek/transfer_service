from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import Depends
from fastapi.responses import RedirectResponse
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from db.settings import get_db_session
from db.repositories.user import UserAlchemy
from db.repositories.token import TokenAlchemy

from auth.env import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from auth.exceptions import credentials_exception, overdue_token_exception, check_used
from auth.schemes import oauth2_scheme_accsess, oauth2_scheme_refresh
from auth.hashing import Hasher



async def authenticate_user(password: str, session: AsyncSession, username: str | None = None, email: str | None = None):
    if username is None:
        user = await UserAlchemy(session).get_for_email(email)
    else:
        user = await UserAlchemy(session).get_for_login(username)
    if user is None:
        return None
    if not Hasher.verify_password(password, user.password):
        return None
    return user


async def create_tokens(data: dict) -> dict:
    to_encode = data.copy()
    jti = str(uuid4())
    expire = datetime.utcnow() + timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire,
                      "typ": "r",
                      "jti": jti})
    refresh_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["typ"] = "a"
    to_encode["exp"] = expire
    access_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_jwt, "refresh_token": refresh_jwt, "token_type": "bearer"}


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme_accsess)], session: Annotated[AsyncSession, Depends(get_db_session)]):
    
    try:
        options = {"require_jti": True,
                   "require_exp": True,
                   "require_sub": True}
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options=options)
    except ExpiredSignatureError:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_exp": False})
        token_from_db = await TokenAlchemy(session).get(payload["jti"])
        if token_from_db is None:
            await TokenAlchemy(session).create({"id": payload["jti"]})
        raise overdue_token_exception
    except JWTError:
        raise credentials_exception
    username = payload["sub"]
    user = await UserAlchemy(session=session).get_for_login(username)
    if user is None:
        raise credentials_exception
    if not await TokenAlchemy(session).get(payload["jti"]) is None:
        raise credentials_exception
    if payload["typ"] == "r":
        raise credentials_exception
    return user


async def replacement(refresh_token: Annotated[str, Depends(oauth2_scheme_refresh)], session: Annotated[AsyncSession, Depends(get_db_session)]):

    try:
        options = {"require_jti": True,
                   "require_exp": True,
                   "require_sub": True}
        payload = jwt.decode(refresh_token, SECRET_KEY, ALGORITHM, options=options)
    except ExpiredSignatureError:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_exp": False})
        await check_used(token=refresh_token, session=session)
        if payload["typ"] == "r":
            return RedirectResponse("/authentication")
        raise overdue_token_exception
    except JWTError:
        raise credentials_exception
    if payload["typ"] == "r":
        await check_used(token=refresh_token, session=session)
        username = payload["sub"]
        if await UserAlchemy(session).get_for_login(username) is None:
            raise credentials_exception
        tokens = await create_tokens(data={"sub": username})
        return tokens
    raise overdue_token_exception