from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import EmailStr
from pydantic.typing import Union

from db.models import User



class UserDAL:
    
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_user_by_login(self, login: str) -> Union[User, None]:
        query = select(User).where(User.login==login, User.is_active==True)
        res = await self.db_session.execute(query)
        return res.scalar_one_or_none()
    
    async def get_user_by_email(self, email: EmailStr) -> Union[User, None]:
        query = select(User).where(User.email==email, User.is_active==True)
        res = await self.db_session.execute(query)
        return res.scalar_one_or_none()
            
    async def create_user(self, login: str, hashed_password: str) -> Union[User, None]:
        new_user = User(
            login=login,
            hashed_password=hashed_password
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user
    
    async def update_user(self, login: str, kwargs) -> Union[User, None]:
        query = update(User).where(User.login==login, User.is_active==True).values(**kwargs).returning(User)
        res = await self.db_session.execute(query)
        return res.scalar_one_or_none()
        
    async def delete_user(self, login: str) -> Union[UUID, None]:
        query = update(User).where(User.login == login, User.is_active==True).values(is_active=False).returning(User.login)
        res = await self.db_session.execute(query)
        return res.scalar_one_or_none()
