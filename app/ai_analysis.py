import re


# =========================================================
# تنظيف النص
# =========================================================

def normalize_text(text):
    text = text.strip()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ة', 'ه')
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    return re.sub(r'\s+', ' ', text)


# =========================================================
# العمر
# =========================================================

def extract_age(text):
    patterns = [
        r'عمري\s*(\d+)',
        r'العمر\s*[:：]?\s*(\d+)',
        r'عمره\s*(\d+)',
        r'عمرها\s*(\d+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return None


# =========================================================
# الجنس
# =========================================================

def extract_gender(text):
    if any(x in text for x in [
        'انثى',
        'بنت',
        'فتاه',
        'امراه',
        'امرأه'
    ]):
        return 'أنثى'

    if any(x in text for x in [
        'ذكر',
        'ولد',
        'رجل'
    ]):
        return 'ذكر'

    return 'غير محدد'


# =========================================================
# الأعراض
# =========================================================

def extract_symptoms(text):

    symptoms = {
        'صداع': [
            'صداع',
            'وجع راس',
            'وجع الراس',
            'الم الراس',
            'الم في الراس',
            'راسي يوجعني',
            'راسي يؤلمني'
        ],

        'حمى': [
            'حمى',
            'حراره',
            'حرارتي مرتفعه',
            'حراره مرتفعه',
            'ارتفاع الحراره',
            'ارتفاع درجه الحراره'
        ],

        'دوخة': [
            'دوخه',
            'دوار',
            'احس بدوخه',
            'اشعر بدوخه',
            'راسي يدور',
            'احس اني دايخه'
        ],

        'تعب': [
            'تعب',
            'ارهاق',
            'خمول',
            'اشعر بالتعب',
            'احس بالتعب',
            'جسمي متعب'
        ],

        'سعال': [
            'سعال',
            'كحه',
            'اكح',
            'اسعل',
            'اسعل كثيرا'
        ],

        'ضيق التنفس': [
            'ضيق التنفس',
            'ضيق نفس',
            'نفسي ضيق',
            'صعوبه التنفس',
            'صعوبه في التنفس',
            'ما اقدر اتنفس',
            'صعب اتنفس'
        ],

        'ألم الصدر': [
            'الم الصدر',
            'الم في الصدر',
            'وجع الصدر',
            'وجع في الصدر',
            'صدري يؤلمني',
            'صدري يوجعني'
        ],

        'غثيان': [
            'غثيان',
            'اشعر بالغثيان',
            'احس بالغثيان'
        ],

        'قيء': [
            'قيء',
            'استفراغ',
            'ترجيع',
            'استفرغ',
            'ارجع'
        ],

        'ألم الحلق': [
            'الم الحلق',
            'الم في الحلق',
            'وجع الحلق',
            'حلقي يؤلمني',
            'حلقي يوجعني',
            'التهاب الحلق'
        ],

        'سيلان الأنف': [
            'سيلان الانف',
            'رشح',
            'انفي يسيل',
            'انفي يرشح'
        ],

        'احتقان': [
            'احتقان',
            'انفي مسدود',
            'انسداد الانف'
        ],

        'ألم البطن': [
            'الم البطن',
            'الم في البطن',
            'وجع البطن',
            'وجع في البطن',
            'بطني يؤلمني',
            'بطني يوجعني',
            'مغص'
        ],

        'ألم الظهر': [
            'الم الظهر',
            'الم في الظهر',
            'وجع الظهر',
            'ظهري يؤلمني',
            'ظهري يوجعني'
        ],

        'خفقان': [
            'خفقان',
            'قلبي يدق بسرعه',
            'نبضات قلبي سريعه',
            'دقات قلبي سريعه'
        ],

        'طفح جلدي': [
            'طفح',
            'طفح جلدي',
            'حساسيه في الجلد',
            'حساسيه بالجلد'
        ],

        'حكة': [
            'حكه',
            'يحكني',
            'حكه جلديه',
            'جلدي يحكني'
        ],

        'تورم': [
            'تورم',
            'انتفاخ',
            'ورم'
        ],

        'نزيف': [
            'نزيف',
            'ينزف',
            'نزف'
        ],

        'قشعريرة': [
            'قشعريره',
            'رعشه',
            'رجفه',
            'ارتجاف'
        ],

        'تعرق': [
            'تعرق',
            'اتعرق',
            'تعرق كثير',
            'تعرق شديد'
        ],

        'تنميل': [
            'تنميل',
            'خدر',
            'تنمل',
            'يدي مخدره',
            'رجلي مخدره'
        ],

        'قلة النوم': [
            'قلة النوم',
            'قله النوم',
            'ما انام كويس',
            'لا انام جيدا',
            'قلة نوم'
        ]
    }

    return [
        name
        for name, keywords in symptoms.items()
        if any(keyword in text for keyword in keywords)
    ]


# =========================================================
# المدة
# =========================================================

def extract_duration(text):

    patterns = [
        (r'منذ\s+يومين', 'يومان'),
        (r'لي\s+يومين', 'يومان'),
        (r'منذ\s+ثلاثة\s+ايام', '3 أيام'),
        (r'منذ\s+ثلاث\s+ايام', '3 أيام'),
        (r'منذ\s+اسبوعين', 'أسبوعان'),
        (r'منذ\s+اسبوع', 'أسبوع'),
        (r'لي\s+اسبوع', 'أسبوع'),
        (r'منذ\s+شهر', 'شهر'),
        (r'منذ\s+ساعه', 'ساعة'),
        (r'منذ\s+ساعة', 'ساعة')
    ]

    for pattern, result in patterns:
        if re.search(pattern, text):
            return result

    match = re.search(
        r'(?:منذ|من|لي)\s+(\d+)\s*'
        r'(يوم|ايام|اسبوع|اسابيع|شهر|اشهر|ساعه|ساعات)',
        text
    )

    if match:
        return f'{match.group(1)} {match.group(2)}'

    if 'اليوم' in text:
        return 'اليوم'

    if 'امس' in text:
        return 'منذ يوم تقريبًا'

    return 'غير محددة'


# =========================================================
# شدة الأعراض
# =========================================================

def extract_severity(text):

    if any(x in text for x in [
        'شديد جدا',
        'شديده جدا',
        'شديد',
        'شديده',
        'قوي جدا',
        'قويه جدا',
        'غير محتمل',
        'ما اقدر',
        'لا استطيع',
        'صعب جدا'
    ]):
        return 'شديدة'

    if any(x in text for x in [
        'متوسط',
        'متوسطه',
        'متوسطة',
        'متوسطا'
    ]):
        return 'متوسطة'

    if any(x in text for x in [
        'خفيف',
        'خفيفه',
        'خفيفة',
        'بسيط',
        'بسيطه',
        'بسيطة'
    ]):
        return 'خفيفة'

    return 'غير محددة'


# =========================================================
# الأعراض المصاحبة
# =========================================================

def extract_associated_symptoms(symptoms):

    associated = []

    for symptom in symptoms:
        if symptom not in associated:
            associated.append(symptom)

    return associated


# =========================================================
# علامات الخطر
# =========================================================

def detect_danger_signs(text):

    danger_signs = []

    if any(x in text for x in [
        'ضيق التنفس',
        'ضيق نفس',
        'نفسي ضيق',
        'صعوبه التنفس',
        'صعوبه في التنفس',
        'ما اقدر اتنفس',
        'صعب اتنفس'
    ]):
        danger_signs.append('ضيق في التنفس')

    if any(x in text for x in [
        'الم الصدر',
        'الم في الصدر',
        'وجع الصدر',
        'وجع في الصدر',
        'صدري يؤلمني',
        'صدري يوجعني'
    ]):
        danger_signs.append('ألم في الصدر')

    if any(x in text for x in [
        'نزيف شديد',
        'نزيف قوي',
        'ينزف كثيرا'
    ]):
        danger_signs.append('نزيف شديد')

    if any(x in text for x in [
        'فقدت الوعي',
        'اغمى علي',
        'اغماء'
    ]):
        danger_signs.append('فقدان الوعي')

    return danger_signs


# =========================================================
# تحديد المسار
# =========================================================

def determine_priority(danger_signs, symptoms):

    if danger_signs:
        return 'high'

    if len(symptoms) >= 2:
        return 'medium'

    return 'low'


def get_priority_ar(priority):

    return {
        'high': 'عالية',
        'medium': 'متوسطة',
        'low': 'منخفضة',
        'unknown': 'غير محددة'
    }.get(priority, 'غير محددة')


def get_recommended_path(priority):

    if priority == 'high':
        return (
            'مسار عاجل: يوصى بطلب المساعدة الطبية العاجلة '
            'وعدم الاكتفاء بالرعاية الذاتية.'
        )

    if priority == 'medium':
        return (
            'مسار المتابعة الطبية: يوصى باستشارة الطبيب '
            'إذا استمرت الأعراض أو ازدادت شدتها.'
        )

    return (
        'مسار الرعاية الذاتية والمتابعة: مراقبة الأعراض '
        'والاهتمام بالراحة، مع استشارة الطبيب عند استمرارها أو تفاقمها.'
    )


# =========================================================
# التحليل الرئيسي
# =========================================================

def analyze_symptoms(text):

    if not text or not text.strip():

        return {
            'age': None,
            'gender': 'غير محدد',
            'detected_symptoms': [],
            'duration': 'غير محددة',
            'associated_symptoms': [],
            'danger_signs': [],
            'severity': 'غير محددة',
            'priority': 'unknown',
            'priority_ar': 'غير محددة',
            'recommended_path': 'لم يتم تحديد المسار.',
            'doctor_summary': 'لم يتم إدخال وصف للحالة.',
            'note': 'هذه النتيجة للدراسة والمساندة ولا تعد تشخيصًا طبيًا.'
        }

    original_text = text
    text = normalize_text(text)

    age = extract_age(text)
    gender = extract_gender(text)

    symptoms = extract_symptoms(text)
    duration = extract_duration(text)
    severity = extract_severity(text)
    danger_signs = detect_danger_signs(text)

    # الأعراض المصاحبة:
    # جميع الأعراض الإضافية غير أول عرض رئيسي
    if len(symptoms) > 1:
        associated_symptoms = symptoms[1:]
    else:
        associated_symptoms = []

    priority = determine_priority(
        danger_signs,
        symptoms
    )

    priority_ar = get_priority_ar(priority)

    recommended_path = get_recommended_path(priority)

    age_text = str(age) if age is not None else 'غير محدد'

    symptoms_text = (
        '، '.join(symptoms)
        if symptoms
        else 'لم يتم التعرف على أعراض محددة'
    )

    associated_text = (
        '، '.join(associated_symptoms)
        if associated_symptoms
        else 'لا توجد أعراض مصاحبة محددة'
    )

    danger_text = (
        '، '.join(danger_signs)
        if danger_signs
        else 'لا توجد علامات خطر واضحة'
    )

    # =====================================================
    # الملخص الذي سيظهر للطبيب
    # =====================================================

    doctor_summary = (
        f'العمر: {age_text}\n'
        f'الجنس: {gender}\n'
        f'الأعراض: {symptoms_text}\n'
        f'المدة: {duration}\n'
        f'الأعراض المصاحبة: {associated_text}\n'
        f'علامات الخطر: {danger_text}\n'
        f'الشدة: {severity}\n'
        f'مستوى الأولوية: {priority_ar}\n'
        f'المسار المقترح: {recommended_path}'
    )

    return {
        'age': age,
        'gender': gender,
        'detected_symptoms': symptoms,
        'duration': duration,
        'associated_symptoms': associated_symptoms,
        'danger_signs': danger_signs,
        'severity': severity,
        'priority': priority,
        'priority_ar': priority_ar,
        'recommended_path': recommended_path,
        'doctor_summary': doctor_summary,
        'original_text': original_text,
        'note': (
            'هذه النتيجة مخصصة للدراسة واختبار الموقع '
            'ولا تعد تشخيصًا طبيًا.'
        )
    }
