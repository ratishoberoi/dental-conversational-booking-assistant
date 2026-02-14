from fastapi import FastAPI
from backend.api.auth_api import router as auth_router
from backend.api.booking_api import router as booking_router
from backend.api.chat_api import router as chat_router
from backend.models.db import SessionLocal
from backend.models.entities import Clinic, Doctor
from datetime import date
from backend.services.scheduler import (
    generate_slots_for_all_doctors,
    get_available_slots_for_service,
)
app = FastAPI(title="Dental Conversational Booking System")
app.include_router(auth_router, prefix="/auth")
app.include_router(booking_router, prefix="/booking")
app.include_router(chat_router, prefix="/chat")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug/clinics")
def list_clinics():
    db = SessionLocal()
    data = db.query(Clinic).all()
    return [{"id": c.id, "name": c.name, "city": c.city} for c in data]


@app.get("/debug/doctors")
def list_doctors():
    db = SessionLocal()
    data = db.query(Doctor).all()
    return [{"id": d.id, "name": d.name, "clinic_id": d.clinic_id} for d in data]

@app.post("/debug/generate-slots")
def gen_slots():
    count = generate_slots_for_all_doctors(date.today())
    return {"created": count}


@app.get("/debug/slots/{service_name}")
def slots_for_service(service_name: str):
    return get_available_slots_for_service(service_name)