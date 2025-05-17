from datetime import timedelta,datetime,timezone
from typing import Annotated
from uuid import UUID,uuid4
from fastapi import Depends
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from app.entites.users import User
from app.models import auth_dto
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging
from dotenv import load_dotenv
import os

load_dotenv("Backend/.env")

SECRECT_KEY = "SECRECT_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')


def verify_password(plain_password:str,password_hashed:str)-> bool:
    return bcrypt_context.verify(plain_password,password_hashed)

def get_password_hash(password:str)->str:
    return bcrypt_context.hash(password)

def authenticate_user(email:str, password:str, db:Session)-> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password,user.password_hash):
        logging.warning(f"Failed authentication attempt for email:{email}")
        return False
    return User


def create_access_token(email:str, user_id:UUID,expires_delta: timedelta)-> str:
    encode = {
        'sub':email,
        'id': str(user_id),
        'exp': datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(encode,SECRECT_KEY,algorithm=ALGORITHM)

def verfiy_token(token:str)-> auth_dto.TokenData:
    try:
        payload = jwt.decode(token, SECRECT_KEY,algorithms=ALGORITHM)
        user_id :str = payload.get('id')
        return auth_dto.TokenData(user_id=user_id)
    except PyJWTError as e:
        logging.error(f"Token verification failed: {str(e)}")
        # TODO: Raise an error from the exceptions
        raise e 
    

def register_user(db: Session, register_user_request: auth_dto.RegisterUserRequest) -> None:
    try:
        user = User(
            id=uuid4(),                                  # optional if you have default
            email=register_user_request.email,
            first_name=register_user_request.first_name, # <-- corrected
            last_name=register_user_request.last_name,
            password_hashed=get_password_hash(register_user_request.password_hashed),  # <-- corrected
        )
        db.add(user)
        db.commit()
    except Exception as e:
        logging.error(f"Failed to register user: {register_user_request.email}. Error: {e}")
        raise
    

def get_current_user(token:Annotated[str, Depends(oauth2_bearer)])-> auth_dto.TokenData:
    return verify_password(token)

CurrentUser = Annotated[auth_dto.TokenData, Depends(get_current_user)]

def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()], db:Session)->auth_dto.Token:
    
    user = authenticate_user(form_data.email, form_data.password,db)
    
    if not user:
        
        # TODO: Replace the string with AuthenticationError
        raise "Failed to get the login access"
    token = create_access_token(user.email,user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return auth_dto.Token(access_token=token, token_type='bearer')
    
    