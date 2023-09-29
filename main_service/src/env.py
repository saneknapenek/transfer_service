from environs import Env



env = Env()
env.read_env(path="/main_service/settings.env")
env.read_env(path="/main_service/.env")

POSTGRESE_USER = env('POSTGRESE_USER')
POSTGRESE_PASSWORD = env('POSTGRESE_PASSWORD')
POSTGRES_DB = env('POSTGRES_DB')
DATABASE_HOST = env('DATABASE_HOST')
DATABASE_PORT = env('DATABASE_PORT')
TEST_POSTGRES_DB = env('TEST_POSTGRES_DB')

DATABASE_URL = f"postgresql+asyncpg://{POSTGRESE_USER}:{POSTGRESE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}"

REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env("REDIS_PORT")

HOST = env('HOST')
