import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

# Get DB URL 
DB_URL = os.environ["POSTGRES_DB_URL"]
REDIS_URL = os.environ["REDIS_URL"]

## create connection to postgresql
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

## create connection to redis 
redis_client = redis.from_url(REDIS_URL)

if(redis_client.ping()):
    print("REDIS CLIENT CONNECTED")
else:
    print("REDIS CLIENT NOT CONNECTED")