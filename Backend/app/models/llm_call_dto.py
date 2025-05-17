from pydantic import BaseModel

class LLM_Request(BaseModel):
    prompt: str 
    temperature: int 
    
class LLM_Response(BaseModel):
    prompt: str