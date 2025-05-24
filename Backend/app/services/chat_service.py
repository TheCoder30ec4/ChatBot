from app.models.chat_dto import chatRequest
from sqlalchemy.orm import Session
from app.entites.chat import Chat
from app.workflows.ChatBot.chains.Chat_llm import get_prompt, chat_llm,create_sessionId
import uuid

# on click on new chat get new session id and commit it into the db 
# using the session id get the chat_llm instance 
# get the prompt_template

def get_sessionId(db:Session,user_id: uuid.UUID):
    session_id = create_sessionId()
    new_chat = Chat(
        session_id= session_id,
        user_id = user_id,
        chat_name=session_id,
        isActive=True
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return {"Session_Id": new_chat.session_id   }