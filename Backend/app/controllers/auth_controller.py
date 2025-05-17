from typing import Annotated
from fastapi import APIRouter,Depends, Request
from starlette import status
from ..models import auth_dto
from ..services import auth_service
from fastapi.security import OAuth2PasswordRequestForm
from ..database.core import DbSession

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/",status_code=status.HTTP_201_CREATED)
async def register_user(request:Request, db:DbSession, register_user_request: auth_dto.RegisterUserRequest):
    auth_service.register_user(db,register_user_request)


@router.post("/token", response_model=auth_dto.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()], db:DbSession):
    return auth_service.login_for_access_token(form_data,db)
