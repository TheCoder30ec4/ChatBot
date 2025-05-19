from app.database.core import SessionLocal
from app.entites.prompts import Prompts
from app.database.constants import CHAT_PROMPT

def seed_prompts():
    db = SessionLocal() 
    
    default_prompt = [
        {"prompt_name":"CHAT-BOT", "system_prompt":CHAT_PROMPT}
    ]
    
    for data in default_prompt:
        existing = db.query(Prompts).filter_by(prompt_name=data["prompt_name"]).first() 
        if not existing:
            prompt = Prompts(**data)
            db.add(prompt)
    
    db.commit()
    db.close()
