import uuid
import logging
from typing import AsyncGenerator, Optional

import psycopg
from psycopg import AsyncConnection
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.callbacks import StreamingStdOutCallbackHandler

from app.database.core import SessionLocal
from app.entites.prompts import Prompts
from app.entites.chat import Chat


TABLE_NAME = "chat_history"
_async_connection: Optional[AsyncConnection] = None



def get_llm(model: str, api_key: str, temperature: float = 0, max_retries: int = 2) -> ChatGroq:
    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_retries=max_retries,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()] 
    )



def get_prompt(prompt_name="CHAT-BOT") -> ChatPromptTemplate:
    db = SessionLocal()
    system_prompt = db.query(Prompts).filter(Prompts.prompt_name == prompt_name).first()
    db.close()

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt.system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])
    return prompt_template



def chain(prompt_template: ChatPromptTemplate, llm_obj: ChatGroq):
    return prompt_template | llm_obj



def create_sessionId() -> str:
    return str(uuid.uuid4())



async def get_async_connection() -> AsyncConnection:
    global _async_connection
    if _async_connection is None or _async_connection.closed:
        connection_string = "postgresql://postgres:postgres@127.0.0.1:5433/posgresDB"
        _async_connection = await psycopg.AsyncConnection.connect(connection_string)
        await PostgresChatMessageHistory.acreate_tables(_async_connection, TABLE_NAME)
        logging.info("Connected using async psycopg3")
    return _async_connection


async def get_chat_memory(session_id: str) -> PostgresChatMessageHistory:
    try:
        connection = await get_async_connection()
        return PostgresChatMessageHistory(
            TABLE_NAME,
            session_id,
            async_connection=connection
        )
    except Exception as e:
        logging.error(f"Failed to create chat memory: {e}")
        raise e



async def chat_llm(
    session_id: str,
    question: str,
    prompt_template: ChatPromptTemplate,
    llm: ChatGroq
) -> Optional[AsyncGenerator[str, None]]:
    db = SessionLocal()
    try:
        chat_row = db.query(Chat).filter(Chat.session_id == session_id).first()
        if not chat_row:
            logging.error("The Session id is not available. Please get a valid session id")
            yield "Invalid session ID"
            return

        chat_row.isActive = True
        db.commit()
        session_id_str = str(chat_row.session_id)

        try:
            chat_memory = await get_chat_memory(session_id_str)
        except Exception as e:
            logging.error(f"Failed to create chat memory: {e}")
            yield f"Error creating chat memory: {str(e)}"
            return

        llm_chain = chain(prompt_template=prompt_template, llm_obj=llm)

        chain_with_memory = RunnableWithMessageHistory(
            llm_chain,
            lambda _: chat_memory,
            input_messages_key="question",
            history_messages_key="history",
        )

        config = {"configurable": {"session_id": session_id_str}}

        try:
            async for chunk in chain_with_memory.astream({"question": question}, config=config):
                yield chunk.content
        except Exception as e:
            logging.error(f"Error during chain invocation: {e}")
            yield f"Error processing request: {str(e)}"

    except Exception as e:
        logging.error(f"Database error: {e}")
        yield f"Database error: {str(e)}"
    finally:
        db.close()
