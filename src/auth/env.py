from environs import Env



env = Env()
env.read_env()


ACCESS_TOKEN_EXPIRE_MINUTES = env("ACCESS_TOKEN_EXPIRE_MINUTES")
SECRET_KEY = env("SECRET_KEY")
ALGORITHM = env("ALGORITHM")