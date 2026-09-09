import re

def _first(patterns, text, default="غير محدد"):
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1)
    return default

def analyze_symptoms(text: str):
    t = text.strip()

    age = _first([r"(?:عمري|العمر)\s*(\d{1,3})\s*(?:سنة|عام)?", r"(\d{1,3})\s*(?:سنة|عام)"], t)
    gender = "أنثى" if re.search(r"أنثى|امرأة|بنت|فتاة", t) else ("ذكر" if re.search(r"ذكر|رجل|ولد|فتى", t) else "غير محدد")

    duration = _first([
        r"(?:منذ|لمدة)\s*(\d+)\s*(يوم|أيام|أسبوع|أسابيع|شهر|ساعات|ساعة)",
        r"(\d+)\s*(يوم|أيام|أسبوع|أسابيع|شهر|ساعات|ساعة)"
    ], t)
    if duration != "غير محدد":
        duration = duration.replace("غير محدد","")
    else:
        duration = "غير محددة"

    symptom_terms = [
        ("صداع", ["صداع","ألم رأس"]),
        ("حرارة", ["حرارة","حمى","درجة الحرارة"]),
        ("سعال", ["سعال","كحة"]),
        ("التهاب الحلق", ["التهاب حلق","ألم الحلق","احتقان الحلق"]),
        ("ألم الصدر", ["ألم في الصدر","ألم الصدر","صدر"]),
        ("ضيق التنفس", ["ضيق التنفس","صعوبة التنفس","ضيق نفس"]),
        ("تعب", ["تعب","إرهاق"]),
        ("دوخة", ["دوخة","دوار"]),
        ("تعرق", ["تعرق","تعرق شديد"]),
        ("احتقان", ["احتقان"]),
        ("قلة النوم", ["قلة النوم","نقص النوم"]),
    ]
    detected=[]
    for name, keys in symptom_terms:
        if any(k in t for k in keys) and name not in detected:
            detected.append(name)

    danger_rules = [
        ("ألم صدر شديد أو متزايد", ["ألم في الصدر","ألم الصدر"]),
        ("ضيق تنفس", ["ضيق التنفس","صعوبة التنفس","ضيق نفس"]),
        ("إغماء أو اضطراب شديد في الوعي", ["إغماء","فقدان الوعي","اضطراب الوعي"]),
        ("ضعف مفاجئ أو اضطراب الكلام", ["ضعف مفاجئ","اضطراب الكلام","صعوبة الكلام"]),
        ("نزيف شديد", ["نزيف شديد","نزيف لا يتوقف"]),
    ]
    danger=[]
    for label, keys in danger_rules:
        if any(k in t for k in keys):
            danger.append(label)

    # عبارات النفي الواضحة تمنع اعتبارها علامة خطر في الأمثلة
    if re.search(r"لا توجد|لا يوجد|بدون|دون", t):
        if re.search(r"علامات خطر|صعوبة في التنفس", t) and not re.search(r"ألم.*صدر|ضيق التنفس|صعوبة التنفس", t):
            danger=[]

    associated=[]
    associated_names={"تعب":"تعب","قلة النوم":"قلة النوم","دوخة":"دوخة","تعرق":"تعرق","احتقان":"احتقان"}
    for k,n in associated_names.items():
        if k in t and n not in detected:
            associated.append(n)

    if danger:
        severity="عالية"
        priority="عاجلة"
        path="تقييم طبي عاجل / طلب المساعدة الطبية عند شدة الأعراض"
    elif len(detected)>=3:
        severity="متوسطة"
        priority="متوسطة"
        path="مراجعة الطبيب حسب الحالة"
    else:
        severity="خفيفة"
        priority="عادية"
        path="المتابعة ومراجعة الطبيب إذا استمرت أو ساءت الأعراض"

    danger_status = "تم رصد علامات خطر: " + "، ".join(danger) if danger else "لم يتم رصد علامات خطر واضحة"

    age_gender = f"{age} سنة / {gender}" if age != "غير محدد" else f"غير محدد / {gender}"

    doctor_summary = (
        f"المريض: {age_gender}. الأعراض: {', '.join(detected) or 'غير محددة'}. "
        f"المدة: {duration}. الأعراض المصاحبة: {', '.join(associated) or 'غير محددة'}. "
        f"علامات الخطر: {danger_status}. الأولوية: {priority}. المسار: {path}."
    )

    return {
        "age": age,
        "gender": gender,
        "detected_symptoms": detected,
        "duration": duration,
        "associated_symptoms": associated,
        "danger_signs": danger,
        "severity": severity,
        "priority": priority,
        "path": path,
        "doctor_summary": doctor_summary,
        "note": "هذه النتيجة للمساندة وتنظيم المعلومات ولا تُعد تشخيصًا طبيًا."
    }


