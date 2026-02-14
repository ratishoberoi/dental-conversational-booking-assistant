from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

from backend.services.conversation_controller import process_message
from backend.services.transcript_logger import log_conversation

router = APIRouter()


class ChatIn(BaseModel):
    history: List[Dict[str, str]]
    message: str


@router.post("/chat")
def chat(data: ChatIn):

    result = process_message(data.history, data.message)

    # -------- transcript logging --------
    log_conversation(
        "demo_user",
        data.history + [
            {"role": "assistant", "content": result["reply"]}
        ]
    )

    return result
