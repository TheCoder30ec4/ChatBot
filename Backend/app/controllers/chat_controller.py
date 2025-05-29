from fastapi import APIRouter,status,Depends,HTTPException
from app.database.core import DbSession
from app.services.chat_service import get_sessionId, llm_chat
from app.services.auth_service import get_current_user
from app.models.auth_dto import TokenData
from app.models.chat_dto import chatRequest


router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/get-session-id",status_code=status.HTTP_200_OK)
def session_id(db:DbSession,user:TokenData = Depends(get_current_user)):
    return get_sessionId(db,user.user_id) # type: ignore

@router.post("/chat-llm",status_code=status.HTTP_200_OK)
def chat(db:DbSession, chat:chatRequest, user:TokenData = Depends(get_current_user)):
    return llm_chat(db=db,session_id=chat.session_id,question=chat.question)