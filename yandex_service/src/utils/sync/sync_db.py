from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from env import DATABASE_SYNC_URL



engine = create_engine(DATABASE_SYNC_URL)

Session = sessionmaker(engine)