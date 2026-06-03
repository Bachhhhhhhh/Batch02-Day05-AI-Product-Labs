from fastapi import APIRouter
from app.api.routes import chat, agent, internal

router = APIRouter()

router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(agent.router, prefix="/agent", tags=["agent"])
router.include_router(internal.router, prefix="/internal", tags=["internal"])
