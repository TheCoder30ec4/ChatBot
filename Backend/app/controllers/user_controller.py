from fastapi import APIRouter,status
from uuid import UUID
from ..database.core import DbSession
from ..models import user_dto
from ..services import user_service
from ..services.auth_service import CurrentUser

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=user_dto.UserResponse)
def get_current_user(current_user: CurrentUser,db:DbSession):
    return user_service.get_user_by_id(db,current_user.get_uuid())

@router.put("/change-password",status_code=status.HTTP_200_OK)
def change_password(change_password:user_dto.ChangePassword,db:DbSession,current_user:CurrentUser):
    user_service.change_password(db,current_user.get_uuid(), change_password)
    
