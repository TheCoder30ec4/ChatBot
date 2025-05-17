from uuid import UUID
from pydantic import BaseModel,EmailStr

class RegisterUserRequest(BaseModel):
    first_name:       str
    last_name:        str
    email:            EmailStr
    password_hashed:  str
    
    
class Token(BaseModel):
    access_token: str 
    token_type: str 
    

class TokenData(BaseModel):
    user_id: str | None = None
    
    def get_uuid(self,)->UUID | None:
        if self.user_id:
            return UUID(self.user_id)
        return None
