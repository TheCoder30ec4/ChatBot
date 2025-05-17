from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session,declarative_base
import os 
from dotenv import load_dotenv
load_dotenv("Backend/.env") 


# Get the Database url from the env
DATABASE_URL="postgresql://admin:admin@localhost:5432/posgresDB"

# Pass the Database url and create an instance with the database
engine = create_engine(DATABASE_URL)

# Make session so that everytime we can interactive the database
SessionLocal = sessionmaker(autoflush=False,autocommit=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close() 

DbSession = Annotated[Session,Depends(get_db)]

