from fastapi import APIRouter, Header, HTTPException
from backend.core.auth import decode_token
from backend.services.booking_service import book_slot_for_user

router = APIRouter()


@router.post("/book")
def book(slot_id: int, service_name: str, authorization: str = Header()):
    token = authorization.split()[1]
    data = decode_token(token)
    user_id = int(data["sub"])

    ok = book_slot_for_user(user_id, slot_id, service_name)

    if not ok:
        raise HTTPException(400, "Slot unavailable")

    return {"status": "confirmed"}
