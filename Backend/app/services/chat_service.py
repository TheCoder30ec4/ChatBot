from app.models.chat_dto import chatRequest
from sqlalchemy.orm import Session
from app.entites.chat import Chat



# on click on new chat get new session id and commit it into the db 
# using the session id get the chat_llm instance 
# 
    