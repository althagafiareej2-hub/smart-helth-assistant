from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.ai_analysis import analyze_symptoms
from app.database import SessionLocal, engine, Base
from app.models import PatientCase


# =========================================================
# إنشاء جداول قاعدة البيانات
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# إنشاء التطبيق
# =========================================================

app = FastAPI(
    title="مسار - المساعد الصحي الذكي",
    version="2.0"
)


# =========================================================
# الملفات الثابتة
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# صفحات HTML
# =========================================================

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# نموذج استقبال الأعراض
# =========================================================

class PatientSymptoms(BaseModel):
    text: str


# =========================================================
# الصفحة الرئيسية
# =========================================================

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================================================
# لوحة المعلومات
# =========================================================

@app.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={}
    )


# =========================================================
# تحليل الأعراض
# =========================================================

@app.post("/analyze")
def analyze(data: PatientSymptoms):

    # -----------------------------------------------------
    # التأكد من وجود نص
    # -----------------------------------------------------

    text = data.text.strip()

    if not text:

        return {
            "case_id": None,
            "age": "غير محدد",
            "gender": "غير محدد",
            "age_gender": "غير محدد",
            "detected_symptoms": [],
            "duration": "غير محددة",
            "associated_symptoms": [],
            "danger_signs": [],
            "danger_status": "لم يتم رصد علامات خطر واضحة",
            "severity": "غير محددة",
            "priority": "unknown",
            "path": "مراجعة الطبيب حسب الحالة",
            "doctor_summary": "لم يتم إدخال وصف للأعراض.",
            "note": "هذه النتيجة للمساندة ولا تُعد تشخيصًا طبيًا."
        }


    # -----------------------------------------------------
    # تشغيل تحليل الذكاء الاصطناعي
    # -----------------------------------------------------

    result = analyze_symptoms(text)


    # -----------------------------------------------------
    # فتح قاعدة البيانات
    # -----------------------------------------------------

    db = SessionLocal()


    try:

        # -------------------------------------------------
        # حفظ الحالة
        # -------------------------------------------------

        case = PatientCase(

            symptoms_text=text,

            detected_symptoms=", ".join(
                result.get("detected_symptoms", [])
            ),

            duration=result.get(
                "duration",
                "غير محددة"
            ),

            severity=result.get(
                "severity",
                "غير محددة"
            ),

            priority=result.get(
                "priority",
                "unknown"
            ),

            doctor_summary=result.get(
                "doctor_summary",
                ""
            )
        )


        db.add(case)

        db.commit()

        db.refresh(case)


        # -------------------------------------------------
        # تجهيز العمر والجنس
        # -------------------------------------------------

        age = result.get(
            "age",
            "غير محدد"
        )

        gender = result.get(
            "gender",
            "غير محدد"
        )


        if age != "غير محدد" and gender != "غير محدد":

            age_gender = f"{age} سنة / {gender}"

        elif age != "غير محدد":

            age_gender = f"{age} سنة / غير محدد"

        elif gender != "غير محدد":

            age_gender = f"غير محدد / {gender}"

        else:

            age_gender = "غير محدد"


        # -------------------------------------------------
        # الأعراض
        # -------------------------------------------------

        symptoms = result.get(
            "detected_symptoms",
            []
        )


        # -------------------------------------------------
        # الأعراض المصاحبة
        # -------------------------------------------------

        associated_symptoms = result.get(
            "associated_symptoms",
            []
        )


        # -------------------------------------------------
        # علامات الخطر
        # -------------------------------------------------

        danger_signs = result.get(
            "danger_signs",
            []
        )


        # -------------------------------------------------
        # حالة علامات الخطر
        # -------------------------------------------------

        if danger_signs:

            danger_status = "تم رصد علامات خطر: " + "، ".join(
                danger_signs
            )

        else:

            danger_status = "لم يتم رصد علامات خطر واضحة"


        # -------------------------------------------------
        # المسار المقترح
        # -------------------------------------------------

        path = result.get(
            "path",
            "مراجعة الطبيب حسب الحالة"
        )


        # -------------------------------------------------
        # إرسال النتيجة للواجهة
        # -------------------------------------------------

        return {

            "case_id": case.id,

            "age": age,

            "gender": gender,

            "age_gender": age_gender,

            "detected_symptoms": symptoms,

            "symptoms": symptoms,

            "duration": result.get(
                "duration",
                "غير محددة"
            ),

            "associated_symptoms": associated_symptoms,

            "danger_signs": danger_signs,

            "danger_status": danger_status,

            "severity": result.get(
                "severity",
                "غير محددة"
            ),

            "priority": result.get(
                "priority",
                "unknown"
            ),

            "path": path,

            "doctor_summary": result.get(
                "doctor_summary",
                ""
            ),

            "note": result.get(
                "note",
                "هذه النتيجة للمساندة ولا تُعد تشخيصًا طبيًا."
            )
        }


    finally:

        # -------------------------------------------------
        # إغلاق قاعدة البيانات
        # -------------------------------------------------

        db.close()


# =========================================================
# رصد الأنماط الصحية
# =========================================================

@app.get("/patterns")
def patterns():

    db = SessionLocal()


    try:

        cases = db.query(PatientCase).all()

    finally:

        db.close()


    # -----------------------------------------------------
    # حساب الفترات الزمنية
    # -----------------------------------------------------

    now = datetime.utcnow()

    recent_start = now - timedelta(
        days=7
    )

    previous_start = now - timedelta(
        days=14
    )


    # -----------------------------------------------------
    # الحالات الحديثة
    # -----------------------------------------------------

    recent = [

        c for c in cases

        if c.created_at
        and c.created_at >= recent_start

    ]


    # -----------------------------------------------------
    # الحالات السابقة
    # -----------------------------------------------------

    previous = [

        c for c in cases

        if c.created_at
        and previous_start <= c.created_at < recent_start

    ]


    # -----------------------------------------------------
    # حساب تكرار الأعراض
    # -----------------------------------------------------

    def count(items):

        output = {}


        for case in items:

            symptoms = (
                case.detected_symptoms
                or ""
            )


            for symptom in symptoms.split(", "):

                if symptom:

                    output[symptom] = (
                        output.get(symptom, 0) + 1
                    )


        return output


    recent_count = count(recent)

    previous_count = count(previous)


    # -----------------------------------------------------
    # اكتشاف الارتفاعات
    # -----------------------------------------------------

    alerts = []


    for symptom, number in recent_count.items():

        old_number = previous_count.get(
            symptom,
            0
        )


        if number >= 3 and number > old_number:

            alerts.append({

                "symptom": symptom,

                "recent_cases": number,

                "previous_cases": old_number,

                "increase": number - old_number,

                "message":
                    f"لوحظ ارتفاع في حالات {symptom}"

            })


    # -----------------------------------------------------
    # النتيجة
    # -----------------------------------------------------

    return {

        "total_cases": len(cases),

        "recent_cases": len(recent),

        "previous_cases": len(previous),

        "recent_symptom_frequency":
            recent_count,

        "previous_symptom_frequency":
            previous_count,

        "alerts": alerts,

        "note":
            "هذه المؤشرات للمساندة ورصد الأنماط الصحية وليست تشخيصًا طبيًا."

    }
