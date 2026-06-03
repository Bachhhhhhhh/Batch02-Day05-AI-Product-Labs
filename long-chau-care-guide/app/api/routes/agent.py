from fastapi import APIRouter, HTTPException, Body
from app.models.schemas import AgentRequest
from app.services.agent_core import HealthcareAgent

router = APIRouter()

@router.post("")
async def agent_endpoint(request: AgentRequest = Body(...)):
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Tin nhắn không được để trống")

    try:
        agent = HealthcareAgent(provider=request.provider, max_iterations=5)
        final_answer = agent.run(user_msg)
        return {
            "answer": final_answer,
            "steps": len(agent.history),
            "trace": agent.history
        }
    except Exception as e:
        return {
            "answer": f"Lỗi hệ thống Agent: {str(e)}",
            "steps": 0,
            "trace": []
        }
