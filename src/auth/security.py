from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import Depends
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .schemes import oauth2_scheme
from .hashing import Hasher
from src.db.settings import get_db_session
from src.db.repositories.user import UserAlchemy
from src.db.repositories.token import TokenAlchemy
from src.auth.env import ALGORITHM, SECRET_KEY
from src.auth.env import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_HOURS
from src.auth.exceptions import credentials_exception, overdue_token_exception, check_used



async def authenticate_user(username: str, password: str, get_user):
    user = await get_user(username)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire,
                      "typ": "a",
                      "jti": str(uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire,
                      "typ": "r",
                      "jti": str(uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_db_session)]):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        if payload["typ"] == "r":
            await check_used(token=token, session=session)
            return replacement(user=username)
    except ExpiredSignatureError:
        jti = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})["jti"]
        await TokenAlchemy(session).create({"token_id": jti})
        raise overdue_token_exception
    except JWTError:
        raise credentials_exception
    user = await UserAlchemy(session=session).get_for_login(username)
    if user is None:
        raise credentials_exception
    return user


async def replacement(user: str):
    data={"sub": user.username}
    access_token = create_access_token(
        data=data, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = create_refresh_token(
        data=data, expires_delta=REFRESH_TOKEN_EXPIRE_HOURS
    )
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}