from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.ai_analysis import analyze_symptoms
from app.database import SessionLocal, engine, Base
from app.models import PatientCase

Base.metadata.create_all(bind=engine)

app = FastAPI(title="مسار - المساعد الصحي الذكي", version="3.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class PatientSymptoms(BaseModel):
    text: str

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.post("/analyze")
def analyze(data: PatientSymptoms):
    text=data.text.strip()
    if not text:
        return {"case_id":None,"age":"غير محدد","gender":"غير محدد","age_gender":"غير محدد",
                "detected_symptoms":[],"duration":"غير محددة","associated_symptoms":[],"danger_signs":[],
                "danger_status":"لم يتم رصد علامات خطر واضحة","severity":"غير محددة","priority":"unknown",
                "path":"مراجعة الطبيب حسب الحالة","doctor_summary":"لم يتم إدخال وصف للأعراض.",
                "note":"هذه النتيجة للمساندة ولا تُعد تشخيصًا طبيًا."}

    result=analyze_symptoms(text)
    db=SessionLocal()
    try:
        case=PatientCase(
            symptoms_text=text,
            age=result.get("age"),
            gender=result.get("gender"),
            detected_symptoms=", ".join(result.get("detected_symptoms",[])),
            duration=result.get("duration"),
            associated_symptoms=", ".join(result.get("associated_symptoms",[])),
            danger_signs=", ".join(result.get("danger_signs",[])),
            severity=result.get("severity"),
            priority=result.get("priority"),
            doctor_summary=result.get("doctor_summary","")
        )
        db.add(case); db.commit(); db.refresh(case)
        age=result.get("age","غير محدد"); gender=result.get("gender","غير محدد")
        age_gender=f"{age} سنة / {gender}" if age!="غير محدد" else f"غير محدد / {gender}"
        danger=result.get("danger_signs",[])
        return {
            "case_id":case.id,"age":age,"gender":gender,"age_gender":age_gender,
            "detected_symptoms":result.get("detected_symptoms",[]),
            "symptoms":result.get("detected_symptoms",[]),
            "duration":result.get("duration","غير محددة"),
            "associated_symptoms":result.get("associated_symptoms",[]),
            "danger_signs":danger,
            "danger_status":"تم رصد علامات خطر: "+ "، ".join(danger) if danger else "لم يتم رصد علامات خطر واضحة",
            "severity":result.get("severity","غير محددة"),
            "priority":result.get("priority","unknown"),
            "path":result.get("path","مراجعة الطبيب حسب الحالة"),
            "doctor_summary":result.get("doctor_summary",""),
            "note":result.get("note","هذه النتيجة للمساندة ولا تُعد تشخيصًا طبيًا.")
        }
    finally:
        db.close()

@app.get("/patterns")
def patterns():
    db=SessionLocal()
    try:
        cases=db.query(PatientCase).all()
    finally:
        db.close()

    now=datetime.utcnow()
    recent_start=now-timedelta(days=7)
    previous_start=now-timedelta(days=14)
    recent=[c for c in cases if c.created_at and c.created_at>=recent_start]
    previous=[c for c in cases if c.created_at and previous_start<=c.created_at<recent_start]

    def count(items):
        out={}
        for c in items:
            for s in (c.detected_symptoms or "").split(", "):
                if s: out[s]=out.get(s,0)+1
        return out

    rc=count(recent); pc=count(previous); alerts=[]
    for symptom,number in rc.items():
        old=pc.get(symptom,0)
        if number>=3 and number>old:
            alerts.append({"symptom":symptom,"recent_cases":number,"previous_cases":old,
                           "increase":number-old,"message":f"لوحظ ارتفاع في حالات {symptom}"})
    return {"total_cases":len(cases),"recent_cases":len(recent),"previous_cases":len(previous),
            "recent_symptom_frequency":rc,"previous_symptom_frequency":pc,"alerts":alerts,
            "note":"هذه المؤشرات للمساندة ورصد الأنماط الصحية وليست تشخيصًا طبيًا."}
