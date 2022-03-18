from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
SQLALCHEMY_DATABASE_URL = 'sqlite:///{}'.format(db_path)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()