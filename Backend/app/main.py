from fastapi import FastAPI
from app.api import register_routers
from app.database.seed import seed_prompts
from app.database.core import Base,engine

app = FastAPI() 

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    seed_prompts()

register_routers(app)