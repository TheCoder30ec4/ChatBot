from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import user_dto
from app.entites import users as user_entity
from app.services.auth_service import verify_password,get_password_hash
import logging


def get_user_by_id(db:Session,user_id:UUID)->user_dto.UserResponse:
    user = db.query(user_entity).filter(user_entity.id == user_id).first() 
    if not user:
        logging.warning(f"User not fount with ID: {user_id}")
        # TODO: Replace with the expection
        raise "User not found"
    logging.info(f"Successfully retrived user with ID:{user_id}")
    return user 

def change_password(db:Session, user_id:UUID, password_change: user_dto.ChangePassword)-> None:
    try:
        user = get_user_by_id(db,user_id)
        if not verify_password(password_change.current_password, user.password_hash):
            logging.warning(f"Invalid current password provided for user ID:{user_id}")
            # TODO: Replace with the custom exception
            raise "Invalid password"
        
        if password_change.new_password != password_change.new_password_confirm:
            logging.warning(f"Password mismacth during change attempt for user_ID: {user_id}")
            #TODO: Replace witj the custom exception
            raise "Password mismatch"
        user.password_hash =  get_password_hash(password_change.new_password)
        db.commit()
        logging.info(f"Successfully changed password for user ID: {user_id}")
    except Exception as e:
        logging.error(f"Error during password change for user ID: {user_id}. Error: {str(e)}")
        raise