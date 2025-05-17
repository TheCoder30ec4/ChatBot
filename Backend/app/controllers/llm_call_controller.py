from app.models import llm_call_dto
from app.services import llm_call_service
from fastapi import APIRouter,status

router = APIRouter(
    prefix="/llm-call",
    tags=["LLM Call"]
)

@router.post("/Ask-llm", response_model=llm_call_dto.LLM_Response, status_code=status.HTTP_200_OK)
def ask_llm(HumanRequestForm:llm_call_dto.LLM_Request):
    return llm_call_service.chat_llm(HumanRequestForm)

