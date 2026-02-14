from datetime import date, timedelta
from backend.models.db import SessionLocal
from backend.models.entities import (
    Service, Clinic, Doctor, DoctorService
)
from backend.services.scheduler import generate_slots_for_doctor


SERVICES = [
    "General Dentistry",
    "Restorative Dentistry",
    "Orthodontics",
    "Periodontal Care",
    "Oral Surgery",
    "Endodontics",
]

CLINICS = [
    ("SmileCare Clinic", "Delhi"),
    ("BrightTooth Center", "Delhi"),
    ("City Dental Hub", "Delhi"),
]

DOCTORS = [
    ("Anita Sharma", 0),
    ("Rahul Mehta", 1),
    ("Vikram Rao", 0),
    ("Neha Kapoor", 2),
    ("Arjun Patel", 1),
    ("Sneha Iyer", 2),
    ("Karan Singh", 0),
    ("Pooja Verma", 1),
    ("Rohit Das", 2),
    ("Meera Nair", 0),
]

DOCTOR_SERVICE_MAP = {
    0: ["General Dentistry"],
    1: ["General Dentistry"],
    2: ["Restorative Dentistry"],
    3: ["Restorative Dentistry"],
    4: ["Orthodontics"],
    5: ["Orthodontics"],
    6: ["Periodontal Care"],
    7: ["Periodontal Care"],
    8: ["Oral Surgery"],
    9: ["Endodontics"],
}


db = SessionLocal()

# ---------- services ----------

service_objs = {}
for name in SERVICES:
    s = db.query(Service).filter_by(name=name).first()
    if not s:
        s = Service(name=name)
        db.add(s)
        db.commit()
        db.refresh(s)
    service_objs[name] = s

print("Services OK")

# ---------- clinics ----------

clinic_objs = []
for name, city in CLINICS:
    c = db.query(Clinic).filter_by(name=name).first()
    if not c:
        c = Clinic(name=name, city=city)
        db.add(c)
        db.commit()
        db.refresh(c)
    clinic_objs.append(c)

print("Clinics OK")

# ---------- doctors ----------

doctor_ids = []

for idx, (doc_name, clinic_idx) in enumerate(DOCTORS):

    d = db.query(Doctor).filter_by(name=doc_name).first()

    if not d:
        d = Doctor(
            name=doc_name,
            clinic_id=clinic_objs[clinic_idx].id
        )
        db.add(d)
        db.commit()
        db.refresh(d)

    doctor_ids.append(d.id)

print("Doctors OK")

# ---------- mappings ----------

for idx, services in DOCTOR_SERVICE_MAP.items():

    doc_id = doctor_ids[idx]

    for svc_name in services:

        svc = service_objs[svc_name]

        exists = db.query(DoctorService).filter_by(
            doctor_id=doc_id,
            service_id=svc.id
        ).first()

        if not exists:
            db.add(DoctorService(
                doctor_id=doc_id,
                service_id=svc.id
            ))
            db.commit()

print("Doctor ↔ Service mappings OK")

db.close()


# ---------- slots (use ids, not ORM objects) ----------

today = date.today()

for doc_id in doctor_ids:
    for offset in range(3):
        generate_slots_for_doctor(doc_id, today + timedelta(days=offset))

print("Slots generated for 3 days")
