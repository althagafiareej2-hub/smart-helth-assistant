from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class PatientCase(Base):
    __tablename__ = "patient_cases"

    id = Column(Integer, primary_key=True, index=True)
    symptoms_text = Column(Text, nullable=False)
    age = Column(String)
    gender = Column(String)
    detected_symptoms = Column(Text)
    duration = Column(String)
    associated_symptoms = Column(Text)
    danger_signs = Column(Text)
    severity = Column(String)
    priority = Column(String)
    doctor_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

