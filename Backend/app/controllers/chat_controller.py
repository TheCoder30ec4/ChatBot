from fastapi import APIRouter,status,Depends,HTTPException
from app.database.core import DbSession
from app.services.chat_service import get_sessionId
from app.services.auth_service import get_current_user
from app.models.auth_dto import TokenData

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/get-session-id",status_code=status.HTTP_200_OK)
def session_id(db:DbSession,user:TokenData = Depends(get_current_user)):
    return get_sessionId(db,user.user_id)