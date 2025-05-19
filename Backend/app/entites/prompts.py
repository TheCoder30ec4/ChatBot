from sqlalchemy import Column,String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.core import Base 

class Prompts(Base):
    __tablename__ = "prompts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_name = Column(String,unique=True,nullable=False)
    system_prompt = Column(String,nullable=False)
    