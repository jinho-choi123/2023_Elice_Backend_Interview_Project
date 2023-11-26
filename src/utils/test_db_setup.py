import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis
from src.db.database import Base

# Get Test DB URL
TEST_DB_URL = os.environ["POSTGRES_TEST_DB_URL"]
TEST_REDIS_URL = os.environ["REDIS_TEST_URL"]

engine = create_engine(TEST_DB_URL)

TEST_SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try: 
        db = TEST_SessionLocal()
        yield db 
    finally:
        db.close()

def override_get_redis_client():
    try:
        redis_client = redis.from_url(TEST_REDIS_URL)
        yield redis_client
    except:
        print("Error occur while executing override_get_redis_client")

@pytest.fixture()
def refresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture()
def refresh_redis():
    redis_client = redis.from_url(TEST_REDIS_URL)
    redis_client.flushdb()
    yield