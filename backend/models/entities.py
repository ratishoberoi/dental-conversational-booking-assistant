from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.models.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from backend.models.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    bookings = relationship("Booking", back_populates="user")


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)

    doctors = relationship("Doctor", back_populates="clinic")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    clinic_id = Column(Integer, ForeignKey("clinics.id"))

    clinic = relationship("Clinic", back_populates="doctors")
    services = relationship("DoctorService", back_populates="doctor")
    slots = relationship("Slot", back_populates="doctor")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    doctors = relationship("DoctorService", back_populates="service")


class DoctorService(Base):
    __tablename__ = "doctor_services"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    service_id = Column(Integer, ForeignKey("services.id"))

    doctor = relationship("Doctor", back_populates="services")
    service = relationship("Service", back_populates="doctors")


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    start_time = Column(DateTime)
    is_booked = Column(Boolean, default=False)

    doctor = relationship("Doctor", back_populates="slots")
    booking = relationship("Booking", back_populates="slot", uselist=False)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    slot_id = Column(Integer, ForeignKey("slots.id"))
    service_name = Column(String)
    created_at = Column(DateTime)

    user = relationship("User", back_populates="bookings")
    slot = relationship("Slot", back_populates="booking")


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String)
    message = Column(String)
    timestamp = Column(DateTime)

class InsuranceInfo(Base):
    __tablename__ = "insurance_info"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String)
    member_id = Column(String)
