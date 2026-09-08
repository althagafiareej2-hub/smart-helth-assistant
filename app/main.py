from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.ai_analysis import analyze_symptoms
from app.database import SessionLocal, engine, Base
from app.models import PatientCase


# إنشاء قاعدة البيانات والجداول
Base.metadata.create_all(bind=engine)


# إنشاء التطبيق
app = FastAPI(
    title="Smart Health Assistant",
    description="مساعد صحي ذكي لتحليل الأعراض وتوجيه المريض",
    version="1.0"
)


# ربط ملفات CSS و JavaScript
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# إعداد صفحات HTML
templates = Jinja2Templates(
    directory="templates"
)


# =========================
# نموذج بيانات المريض
# =========================

class PatientSymptoms(BaseModel):
    text: str


# =========================
# الصفحة الرئيسية
# =========================

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================
# تحليل الأعراض
# =========================

@app.post("/analyze")
def analyze(data: PatientSymptoms):

    # تحليل الأعراض
    result = analyze_symptoms(data.text)

    # فتح قاعدة البيانات
    db = SessionLocal()

    try:

        # إنشاء حالة جديدة
        case = PatientCase(
            symptoms_text=data.text,

            detected_symptoms=", ".join(
                result["detected_symptoms"]
            ),

            duration=result["duration"],

            severity=result["severity"],

            priority=result["priority"],

            doctor_summary=result["doctor_summary"]
        )

        # حفظ الحالة
        db.add(case)

        db.commit()

        db.refresh(case)

        return {
            "case_id": case.id,
            **result
        }

    finally:

        db.close()


# =========================
# رصد الأنماط
# =========================

@app.get("/patterns")
def detect_patterns():

    db = SessionLocal()

    try:

        cases = db.query(PatientCase).all()

    finally:

        db.close()


    # الوقت الحالي
    now = datetime.utcnow()


    # آخر 7 أيام
    recent_start = now - timedelta(days=7)


    # من 7 إلى 14 يوم
    previous_start = now - timedelta(days=14)


    recent_cases = []

    previous_cases = []


    # تقسيم الحالات حسب الفترة
    for case in cases:

        if not case.created_at:
            continue


        if case.created_at >= recent_start:

            recent_cases.append(case)


        elif case.created_at >= previous_start:

            previous_cases.append(case)


    # =========================
    # أعراض آخر 7 أيام
    # =========================

    recent_counts = {}


    for case in recent_cases:

        if not case.detected_symptoms:
            continue


        symptoms = case.detected_symptoms.split(", ")


        for symptom in symptoms:

            recent_counts[symptom] = (
                recent_counts.get(symptom, 0) + 1
            )


    # =========================
    # أعراض الفترة السابقة
    # =========================

    previous_counts = {}


    for case in previous_cases:

        if not case.detected_symptoms:
            continue


        symptoms = case.detected_symptoms.split(", ")


        for symptom in symptoms:

            previous_counts[symptom] = (
                previous_counts.get(symptom, 0) + 1
            )


    # =========================
    # اكتشاف الارتفاع
    # =========================

    alerts = []


    for symptom, recent_count in recent_counts.items():

        previous_count = previous_counts.get(
            symptom,
            0
        )


        if (
            recent_count >= 3
            and recent_count > previous_count
        ):

            alerts.append({

                "symptom": symptom,

                "recent_cases": recent_count,

                "previous_cases": previous_count,

                "increase":
                    recent_count - previous_count,

                "message":
                    f"لوحظ ارتفاع في حالات {symptom}"
            })


    return {

        "total_cases": len(cases),

        "recent_cases": len(recent_cases),

        "previous_cases": len(previous_cases),

        "recent_symptom_frequency":
            recent_counts,

        "previous_symptom_frequency":
            previous_counts,

        "alerts": alerts,

        "note":
            "هذه المؤشرات للمساندة ورصد الأنماط الصحية "
            "وليست تشخيصًا طبيًا."
    }
