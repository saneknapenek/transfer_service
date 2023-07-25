from abc import ABC, abstractmethod



class Repository(abs):
    
    @abstractmethod
    async def create():
        raise NotImplementedError
    
    @abstractmethod
    async def update():
        raise NotImplementedError
    
    @abstractmethod
    async def delete():
        raise NotImplementedError
    
    @abstractmethod
    async def get_for_id():
        raise NotImplementedError
    

class Extended(Repository):

    @abstractmethod
    async def delete_permanently():
        raise NotImplementedError
    
    @abstractmethod
    async def get():
        raise NotImplementedError


class SQLAlchemyRepo():
    pass