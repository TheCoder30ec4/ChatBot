from pydantic import BaseModel

class PromptResponse(BaseModel):
    prompt_name:str 
    system_prompt:str
    
class PromptWrapper(BaseModel):
    id:str 
    prompt: PromptResponse
    
class NewPromptRequest(BaseModel):
    prompt_name:str
    system_prompt:str
    
    
    