from fastapi import FastAPI
from app.api import register_routers


app = FastAPI() 

register_routers(app)