from sqlalchemy.orm import Session
from app.models.prompt_dto import PromptWrapper,PromptResponse,NewPromptRequest
from app.entites.prompts import Prompts
from typing import List
from uuid import uuid4
import logging


def get_prompts(db:Session)->List[PromptWrapper]:
    prompts = db.query(Prompts).all()
    
    return [
        PromptWrapper(
            id=str(prompt.id),
            prompt=PromptResponse(
                prompt_name=prompt.prompt_name,
                system_prompt=prompt.system_prompt
            )
        )
        for prompt in prompts
    ]
    
def get_prompt(db:Session,prompt_name:str)->PromptResponse | str:
    try:
        
        prompt = db.query(Prompts).filter(Prompts.prompt_name == prompt_name).first()
        if not prompt:
            return f"Failed to get the prompt name"
        return PromptResponse(
            prompt_name=prompt.prompt_name,
            system_prompt=prompt.system_prompt
        )
    except Exception as e:
        return f"Failed to get the prompt name. Error{e}"
    
def get_prompt_orm(db:Session,prompt_name:str)-> Prompts | None:
    try:
        return db.query(Prompts).filter(Prompts.prompt_name == prompt_name).first()
    except Exception as e:
        logging.error(f"Failed to get the prompt_name {prompt_name}. Error {e}")
        raise
    
def post_prompt(db:Session,prompt:NewPromptRequest)-> str | None:
    try:
        new_prompt = Prompts(
            id=uuid4(),
            prompt_name=prompt.prompt_name,
            system_prompt=prompt.system_prompt
        )
        db.add(new_prompt)
        db.commit()
        result = db.query(Prompts).filter_by(prompt_name=prompt.prompt_name).first()
        if not result:
            logging.error(f"Failed to add new prompt")
            return None
        return result
    except Exception as e:
        logging.error(f"Failed to add new prompt. Error:{e}")
        raise
        
        
def delete_prompt(db:Session,prompt_name:str)-> bool:
    try:
        prompt = db.query(Prompts).filter(Prompts.prompt_name == prompt_name).first()
        if not prompt:
            return False
        db.delete(prompt)
        db.commit()
        return True
    except Exception as e:
        logging.error(f"Failed to delete the prompt. Erorr:{e}")
        raise
    


def change_prompt(db: Session, prompt: PromptResponse) -> bool:
    try:
        prev_prompt = get_prompt_orm(db, prompt.prompt_name)
        print(prev_prompt)
        if not prev_prompt:
            return False  
        prev_prompt.system_prompt = prompt.system_prompt  
        # db.add(prev_prompt)
        db.commit()
        return True
    except Exception as e:
        logging.error(f"Failed to change the prompt. Error: {e}")
        return False

        
        
        