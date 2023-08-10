from redis import Redis
from redis_om import HashModel, Field



class Base(HashModel):
    class Meta:
        database = Redis(port=6379)
        global_key_prefix = "Yandex"


class AuthModel(Base):
    user: int = Field(index=True)
    token_type: str
    token: str
