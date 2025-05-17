from fastapi import FastAPI
from app.controllers.auth_controller import router as auth_router 
from app.controllers.user_controller import router as user_router
from app.controllers.llm_call_controller import router as llm_router


def register_routers(app:FastAPI):
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(llm_router)