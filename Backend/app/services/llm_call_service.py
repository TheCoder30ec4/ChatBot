from app.models.llm_call_dto import LLM_Request, LLM_Response
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)

def chat_llm(humanMessage: LLM_Request) -> LLM_Response:
    llm = ChatGroq(
        model="mistral-saba-24b",
        temperature=humanMessage.temperature,
        api_key="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"
    )
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a helpful AI assistant. You have point-wise information for "
            "whatever the user asks."
        ),
        MessagesPlaceholder(variable_name="message")
        
    ])
    
    messages = [HumanMessage(content=humanMessage.prompt)]
    
    
    
    
    
    chain = chat_prompt | llm | StrOutputParser()

    raw_output: str = chain.invoke({"message": messages})

    return LLM_Response(prompt=raw_output)
