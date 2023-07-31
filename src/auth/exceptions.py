from uuid import uuid4

from fastapi.exceptions import HTTPException
from fastapi import status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.env import ALGORITHM, SECRET_KEY
from src.db.repositories.token import TokenAlchemy



credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

overdue_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials. Send a refresh token",
    headers={"WWW-Authenticate": "Bearer"}
)

used_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Used token.",
    headers={"WWW-Authenticate": "Bearer"}
)

async def check_used(token: str, session: AsyncSession):
    payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
    res = await TokenAlchemy(session).get_for_token_id(payload["jti"])
    if res.scalar_one_or_none() is None:
        await TokenAlchemy(session).create({"token_id": str(uuid4())})
        raise used_token_exception
    return True