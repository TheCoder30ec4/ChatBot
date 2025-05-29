from sqlalchemy.orm import Session
from app.entites.chat import Chat
from app.workflows.ChatBot.chains.Chat_llm import  chat_llm,create_sessionId, get_llm,get_prompt #type: ignore
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


def llm_chat(db:Session,session_id:str, question:str)-> str: #type: ignore
    prompt_template = get_prompt()
    llm = get_llm(model="mistral-saba-24b",api_key="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")
    return chat_llm(session_id=session_id,question=question,prompt_template=prompt_template,llm=llm)# type: ignore
