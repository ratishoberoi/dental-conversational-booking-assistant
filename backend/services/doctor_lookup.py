from backend.models.db import SessionLocal
from backend.models.entities import Doctor, Clinic, Service, DoctorService


def get_doctors_for_service(service_name: str):

    db = SessionLocal()

    try:
        svc = db.query(Service).filter_by(name=service_name).first()
        if not svc:
            return []

        links = db.query(DoctorService).filter_by(
            service_id=svc.id
        ).all()

        result = []

        for link in links:
            d = db.query(Doctor).filter_by(id=link.doctor_id).first()
            if not d:
                continue

            clinic = db.query(Clinic).filter_by(id=d.clinic_id).first()

            result.append({
                "id": d.id,
                "name": d.name,
                "specialty": service_name,          # derived, not from doctor table
                "clinic_name": clinic.name if clinic else "Unknown"
            })

        return result

    finally:
        db.close()
