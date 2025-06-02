from fastapi import FastAPI
from app.tools.math_tool import router as math_router

def register_routers(app: FastAPI):
    app.include_router(math_router)
