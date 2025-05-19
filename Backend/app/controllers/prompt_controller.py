from fastapi import APIRouter,status,Depends, HTTPException
from app.database.core import DbSession
from app.services.prompt_service import get_prompts,post_prompt,delete_prompt,get_prompt,change_prompt
from app.models.prompt_dto import PromptWrapper,NewPromptRequest,PromptResponse
from app.services.auth_service import get_current_user



router = APIRouter(
    prefix="/prompts",
    tags=['Prompt Library'],
    dependencies=[Depends(get_current_user)]
)

@router.get("/list-prompts", status_code=status.HTTP_200_OK, response_model=list[PromptWrapper])
def list_prompts(db:DbSession):
    return get_prompts(db)

@router.get("/list-prompts/{prompt_name}", status_code=status.HTTP_200_OK, response_model=PromptResponse)
def getByName(db:DbSession, prompt_name:str):
    return get_prompt(db,prompt_name)
    
@router.post("/new-prompt", status_code=status.HTTP_201_CREATED)
async def new_prompt(db: DbSession, prompt:NewPromptRequest):
    return post_prompt(db,prompt)

@router.put("/change-prompt",status_code=status.HTTP_201_CREATED)
async def put_prompt(db:DbSession,prompt:PromptResponse):
    new_prompt = change_prompt(db,prompt)
    if not new_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with Prompt Name {prompt.prompt_name} not found"
        )
    return {"message": f"Prompt with {prompt.prompt_name} updated Successfully"}


@router.delete("/delete/{prompt_name}", status_code=status.HTTP_200_OK)
def remove_prompt(db:DbSession,prompt_name:str):
    delete = delete_prompt(db,prompt_name)
    if not delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_name} not found"
        )
    return {"message": f"Prompt with ID {prompt_name} deleted successfully"}
    
    
