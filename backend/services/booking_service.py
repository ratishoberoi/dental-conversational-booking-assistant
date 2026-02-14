from datetime import datetime
from backend.models.db import SessionLocal
from backend.models.entities import Slot, Booking


def book_slot_for_user(user_id: int, slot_id: int, service_name: str):
    db = SessionLocal()

    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot or slot.is_booked:
        db.close()
        return False

    slot.is_booked = True

    booking = Booking(
        user_id=user_id,
        slot_id=slot_id,
        service_name=service_name,
        created_at=datetime.utcnow()
    )

    db.add(booking)
    db.commit()
    db.close()

    return True
