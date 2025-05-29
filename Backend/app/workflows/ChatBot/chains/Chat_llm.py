import uuid
import logging

import psycopg2
import psycopg  # For modern psycopg3 connection
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.database.core import SessionLocal
from app.entites.prompts import Prompts
from app.entites.chat import Chat

# 1. Define your table name (must match the name you created above)
TABLE_NAME = "chat_history"

# Global connection for reuse
_connection = None


llm = ChatGroq(
    model="mistral-saba-24b",
    api_key="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"
)


def get_llm(model: str, api_key: str, temperature: float = 0, max_retries: int = 2) -> ChatGroq:
    return ChatGroq(model=model, api_key=api_key, temperature=temperature, max_retries=max_retries)


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


def get_connection():
    """Get or create a database connection using psycopg (not psycopg2)"""
    global _connection
    if _connection is None or _connection.closed:
        connection_string = "postgresql://postgres:postgres@127.0.0.1:5433/posgresDB"
        try:
            # Try psycopg3 first (recommended for langchain-postgres)
            _connection = psycopg.connect(connection_string)
            # Ensure table exists
            PostgresChatMessageHistory.create_tables(_connection, TABLE_NAME)
            logging.info("Connected using psycopg3")
        except (ImportError, Exception) as e:
            logging.warning(f"psycopg3 failed: {e}, falling back to psycopg2")
            # Fallback to psycopg2 if psycopg3 is not available
            _connection = psycopg2.connect(connection_string)
            # Create table manually for psycopg2
            create_table_if_not_exists(_connection)
    return _connection


def create_table_if_not_exists(connection):
    """Create chat history table if it doesn't exist (for psycopg2 fallback)"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    message JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        connection.commit()
        logging.info(f"Table '{TABLE_NAME}' created or already exists")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        connection.rollback()


def get_chat_memory(session_id: str) -> PostgresChatMessageHistory:
    """
    Create PostgresChatMessageHistory with proper connection.
    Only sync_connection is supported as a parameter.
    """
    try:
        connection = get_connection()
        return PostgresChatMessageHistory(
            TABLE_NAME,  # positional argument
            session_id,  # positional argument
            sync_connection=connection
        )
    except Exception as e:
        logging.error(f"Failed to create chat memory: {e}")
        raise e


def chat_llm(
    session_id: str,
    question: str,
    prompt_template: ChatPromptTemplate,
    llm: ChatGroq
) -> str:
    db = SessionLocal()
    try:
        chat_row = db.query(Chat).filter(Chat.session_id == session_id).first()
        if not chat_row:
            logging.error("The Session id is not available. Please get a valid session id")
            return "Invalid session ID"

        # Mark the chat row as active
        chat_row.isActive = True
        db.commit()

        # Convert session_id to string to ensure it's not causing type issues
        session_id_str = str(chat_row.session_id)

        # Get chat memory with error handling
        try:
            chat_memory = get_chat_memory(session_id_str)
        except Exception as e:
            logging.error(f"Failed to create chat memory: {e}")
            return f"Error creating chat memory: {str(e)}"

        llm_chain = chain(prompt_template=prompt_template, llm_obj=llm)

        chain_with_memory = RunnableWithMessageHistory(
            llm_chain,
            lambda _: chat_memory,
            input_messages_key="question",
            history_messages_key="history"
        )

        config = {"configurable": {"session_id": session_id_str}}
        
        try:
            response = chain_with_memory.invoke({"question": question}, config=config)
            return response
        except Exception as e:
            logging.error(f"Error during chain invocation: {e}")
            return f"Error processing request: {str(e)}"
            
    except Exception as e:
        logging.error(f"Database error: {e}")
        return f"Database error: {str(e)}"
    finally:
        db.close()