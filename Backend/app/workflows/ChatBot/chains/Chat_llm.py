import sys
import os
import uuid
import logging

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.database.core import SessionLocal
from app.entites.prompts import Prompts
from app.entites.chat import Chat

# Initialize LLM
llm = ChatGroq(
    model="mistral-saba-24b",
    api_key="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"
)

def get_prompt(prompt_name="CHAT-BOT") -> ChatPromptTemplate:
    db = SessionLocal()
    system_prompt = db.query(Prompts).filter(Prompts.prompt_name == prompt_name).first()
    db.close()

    print(system_prompt.system_prompt)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt.system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    return prompt_template

def chain(llm, prompt_template: ChatPromptTemplate):
    return prompt_template | llm

def create_sessionId():
    return str(uuid.uuid4())

def get_chat_memory(session_id: str):
    connection_string = "postgresql://postgres:postgres@localhost:5433/postgresDB"
    return PostgresChatMessageHistory(session_id=session_id, connection_string=connection_string)

def chat_llm(session_id: str, question: str, prompt_template: ChatPromptTemplate, llm) -> str:
    db = SessionLocal()
    chat_row = db.query(Chat).filter(Chat.session_id == session_id).first()

    if not chat_row:
        logging.error(f"The Session id is not available. Please get a valid session id")
        return "Invalid session ID"
    else:
        chat_row.isActive = True
        db.commit()

        chat_memory = get_chat_memory(chat_row.session_id)
        llm_chain = chain(llm=llm, prompt_template=prompt_template)

        chain_with_memory = RunnableWithMessageHistory(
            llm_chain,
            lambda _: chat_memory,
            input_messages_key="question",
            history_messages_key="history"
        )

        config = {"configurable": {"session_id": session_id}}
        response = chain_with_memory.invoke({"question": question}, config=config)

        return response
