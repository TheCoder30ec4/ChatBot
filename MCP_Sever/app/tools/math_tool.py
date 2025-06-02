from fastapi import APIRouter
import math

router = APIRouter(prefix='/math_tool', tags=['tools'])

def safe_eval(expr: str) -> float:
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    return eval(expr, {"__builtins__": {}}, allowed_names)

@router.get("/", operation_id="math_tool", summary="Math tool for simple math calculations")
async def math_tool(query: str):
    try:
        answer = safe_eval(query)
        return {"result": f"{answer}"}
    except Exception as e:
        return {"error": str(e)}
