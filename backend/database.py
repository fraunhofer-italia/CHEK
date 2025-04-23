
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config
from sqlalchemy import create_engine

POSTGRES_DB = config.POSTGRES_DB
POSTGRES_USER = config.POSTGRES_USER
POSTGRES_PASSWORD = config.POSTGRES_PASSWORD
POSTGRES_HOST = config.POSTGRES_HOST
POSTGRES_PORT = config.POSTGRES_PORT 

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
