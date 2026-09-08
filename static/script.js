// ============================================================
// بيانات آخر تحليل
// ============================================================

let lastAnalysis = {
    text: '',
    age: 'غير محدد',
    gender: 'غير محدد',
    symptoms: '—',
    duration: 'غير محددة',
    associatedSymptoms: 'لا توجد أعراض مصاحبة محددة',
    dangerSigns: 'لا توجد علامات خطر واضحة',
    priority: 'غير محددة',
    path: 'مراجعة الطبيب حسب الحالة'
};


// ============================================================
// التنقل بين الشاشات
// ============================================================

function showScreen(id) {

    document
        .querySelectorAll('.screen')
        .forEach(screen => {
            screen.classList.remove('active-screen');
        });

    const element = document.getElementById(id);

    if (element) {
        element.classList.add('active-screen');
    }

    window.scrollTo(0, 0);
}


// ============================================================
// بدء التحليل
// ============================================================

async function startAnalysis() {

    const input = document.getElementById('symptoms');

    const text = input.value.trim();

    if (!text) {
        alert('فضلاً اكتب وصف حالتك الصحية أولاً.');
        return;
    }

    lastAnalysis.text = text;

    showScreen('processing');

    const bar = document.getElementById('progressBar');

    if (bar) {
        bar.style.width = '8%';
    }

    try {

        const response = await fetch('/analyze', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                text: text
            })
        });


        if (!response.ok) {
            throw new Error('حدث خطأ أثناء الاتصال بالخادم.');
        }


        const result = await response.json();


        // ====================================================
        // تحديث شريط التحليل
        // ====================================================

        if (bar) {

            bar.style.width = '35%';

            setTimeout(() => {
                bar.style.width = '65%';
            }, 300);

            setTimeout(() => {
                bar.style.width = '85%';
            }, 600);

            setTimeout(() => {
                bar.style.width = '100%';
            }, 900);
        }


        // ====================================================
        // حفظ نتيجة التحليل
        // ====================================================

        lastAnalysis.age =
            result.age !== null &&
            result.age !== undefined
                ? result.age
                : 'غير محدد';


        lastAnalysis.gender =
            result.gender ||
            'غير محدد';


        lastAnalysis.symptoms =
            result.detected_symptoms &&
            result.detected_symptoms.length
                ? result.detected_symptoms.join('، ')
                : 'لم يتم التعرف على أعراض محددة';


        lastAnalysis.duration =
            result.duration ||
            'غير محددة';


        lastAnalysis.associatedSymptoms =
            result.associated_symptoms &&
            result.associated_symptoms.length
                ? result.associated_symptoms.join('، ')
                : 'لا توجد أعراض مصاحبة محددة';


        lastAnalysis.dangerSigns =
            result.danger_signs &&
            result.danger_signs.length
                ? result.danger_signs.join('، ')
                : 'لا توجد علامات خطر واضحة';


        lastAnalysis.priority =
            result.priority_ar ||
            'غير محددة';


        lastAnalysis.path =
            result.recommended_path ||
            'مراجعة الطبيب حسب الحالة';


        // ====================================================
        // تحديث الملخص
        // ====================================================

        setTimeout(() => {

            updateSummary();

            updateDoctorPage();

            showScreen('summary');

        }, 1100);


    } catch (error) {

        console.error(error);

        alert(
            'حدث خطأ أثناء تحليل الحالة. تأكدي من تشغيل الخادم.'
        );

        showScreen('analysis');
    }
}


// ============================================================
// تحديث صفحة ملخص الحالة
// ============================================================

function updateSummary() {

    const card =
        document.getElementById('summaryData');

    if (!card) {
        return;
    }


    const values =
        card.querySelectorAll('div b');


    if (values.length >= 6) {

        values[0].textContent =
            `${lastAnalysis.age} / ${lastAnalysis.gender}`;


        values[1].textContent =
            lastAnalysis.symptoms;


        values[2].textContent =
            lastAnalysis.duration;


        values[3].textContent =
            lastAnalysis.associatedSymptoms;


        values[4].textContent =
            lastAnalysis.dangerSigns;


        values[5].textContent =
            lastAnalysis.path;
    }
}


// ============================================================
// تحديث صفحة الطبيب
// ============================================================

function updateDoctorPage() {

    const ageGender =
        document.getElementById('docAgeGender');

    const symptoms =
        document.getElementById('docSymptoms');

    const duration =
        document.getElementById('docDuration');

    const associated =
        document.getElementById('docAssociated');

    const danger =
        document.getElementById('docDanger');

    const route =
        document.getElementById('docRoute');


    if (ageGender) {
        ageGender.textContent =
            `${lastAnalysis.age} / ${lastAnalysis.gender}`;
    }


    if (symptoms) {
        symptoms.textContent =
            lastAnalysis.symptoms;
    }


    if (duration) {
        duration.textContent =
            lastAnalysis.duration;
    }


    if (associated) {
        associated.textContent =
            lastAnalysis.associatedSymptoms;
    }


    if (danger) {
        danger.textContent =
            lastAnalysis.dangerSigns;
    }


    if (route) {
        route.textContent =
            lastAnalysis.path;
    }
}


// ============================================================
// النوافذ المنبثقة
// ============================================================

function openModal(type) {

    const modal =
        document.getElementById('modal');

    const title =
        document.getElementById('modalTitle');

    const text =
        document.getElementById('modalText');


    modal.classList.add('show');


    if (type === 'nearest') {

        title.textContent =
            'أقرب موعد';

        text.textContent =
            'أقرب موعد مقترح حسب المواعيد المتاحة.';

    } else {

        title.textContent =
            'حجز موعد';

        text.textContent =
            'اختر الموعد المناسب لك.';
    }
}


function closeModal() {

    document
        .getElementById('modal')
        .classList.remove('show');
}


function confirmAppointment() {

    closeModal();

    alert(
        'تم تأكيد الموعد بنجاح'
    );
}
