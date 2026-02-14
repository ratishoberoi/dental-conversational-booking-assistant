from datetime import datetime, timedelta, time
from backend.models.db import SessionLocal
from backend.models.entities import Doctor, Slot, Service, DoctorService


WORK_START = time(hour=9, minute=0)
WORK_END = time(hour=17, minute=0)
SLOT_MINUTES = 15


# ---------------- SLOT GENERATION ----------------

def generate_slots_for_doctor(doctor_id: int, day):
    db = SessionLocal()

    try:
        start_dt = datetime.combine(day, WORK_START)
        end_dt = datetime.combine(day, WORK_END)

        current = start_dt
        created = 0

        while current < end_dt:
            exists = db.query(Slot).filter(
                Slot.doctor_id == doctor_id,
                Slot.start_time == current
            ).first()

            if not exists:
                db.add(Slot(
                    doctor_id=doctor_id,
                    start_time=current,
                    is_booked=False
                ))
                created += 1

            current += timedelta(minutes=SLOT_MINUTES)

        db.commit()
        return created

    finally:
        db.close()


def generate_slots_for_all_doctors(day):
    db = SessionLocal()
    try:
        doctors = db.query(Doctor).all()
    finally:
        db.close()

    total = 0
    for d in doctors:
        total += generate_slots_for_doctor(d.id, day)

    return total


# ---------------- SLOT QUERY ----------------

def get_available_slots_for_service(service_name: str, doctor_id: int | None = None, limit: int = 20):

    db = SessionLocal()

    try:
        svc = db.query(Service).filter(Service.name == service_name).first()
        if not svc:
            return []

        doc_links = db.query(DoctorService).filter(
            DoctorService.service_id == svc.id
        ).all()

        doctor_ids = [l.doctor_id for l in doc_links]

        if doctor_id:
            doctor_ids = [doctor_id] if doctor_id in doctor_ids else []

        if not doctor_ids:
            return []

        slots = db.query(Slot).filter(
            Slot.doctor_id.in_(doctor_ids),
            Slot.is_booked == False
        ).order_by(Slot.start_time).limit(limit).all()

        from backend.models.entities import Doctor

        result = []

        for s in slots:
            d = db.query(Doctor).filter_by(id=s.doctor_id).first()

            result.append({
                "slot_id": s.id,
                "doctor_id": s.doctor_id,
                "doctor_name": d.name if d else f"Doctor {s.doctor_id}",
                "time": s.start_time.isoformat()
            })


        return result

    finally:
        db.close()


# ---------------- BOOKING ----------------

def book_slot(slot_id: int):

    db = SessionLocal()

    try:
        slot = db.query(Slot).filter(Slot.id == slot_id).first()

        if not slot:
            return False, "Slot not found"

        if slot.is_booked:
            return False, "Already booked"

        slot.is_booked = True
        db.commit()

        return True, "Booked"

    finally:
        db.close()
