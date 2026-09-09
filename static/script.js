let lastAnalysis = {symptoms:"", result:null};

const examples = [
"عمري 22 سنة، أنثى، أعاني من صداع خفيف منذ يومين مع تعب وقلة نوم، ولا توجد علامات خطر.",
"عمري 45 سنة، ذكر، أعاني من ألم في الصدر وضيق في التنفس منذ ساعتين، مع تعرق ودوخة، وأشعر أن الألم يزداد.",
"عمري 8 سنوات، أنثى، أعاني من حرارة وسعال منذ يومين مع احتقان الحلق، ولا توجد صعوبة في التنفس أو علامات خطر."
];

function showScreen(id){
    document.querySelectorAll(".screen").forEach(s=>s.classList.remove("active-screen"));
    const el=document.getElementById(id);
    if(el) el.classList.add("active-screen");
    window.scrollTo(0,0);
}

function loadExample(i){
    const input=document.getElementById("symptoms");
    if(input){
        input.value=examples[i];
        showScreen("analysis");
        input.focus();
    }
}

async function startAnalysis(){
    const input=document.getElementById("symptoms");
    const text=(input?.value||"").trim();
    if(!text){
        alert("اكتب وصف الحالة أولاً.");
        return;
    }

    lastAnalysis.symptoms=text;
    showScreen("processing");

    const bar=document.getElementById("progressBar");
    const percent=document.getElementById("progressPercent");
    let p=0;
    const timer=setInterval(()=>{p=Math.min(p+8,88);bar.style.width=p+"%";percent.textContent=p+"%";},120);

    try{
        const response=await fetch("/analyze",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({text})
        });
        if(!response.ok) throw new Error("analysis failed");
        const result=await response.json();
        clearInterval(timer);
        bar.style.width="100%"; percent.textContent="100%";
        lastAnalysis.result=result;
        setTimeout(()=>{updateSummary(result);showScreen("summary");},450);
    }catch(error){
        clearInterval(timer);
        alert("تعذر تحليل الحالة. تأكدي من تشغيل الخادم.");
        showScreen("analysis");
    }
}

function val(v, fallback="غير محدد"){
    if(Array.isArray(v)) return v.length?v.join("، "):fallback;
    return (v===null||v===undefined||v==="")?fallback:String(v);
}

function updateSummary(r){
    document.getElementById("summaryAgeGender").textContent=val(r.age_gender);
    document.getElementById("summarySymptoms").textContent=val(r.detected_symptoms);
    document.getElementById("summaryDuration").textContent=val(r.duration,"غير محددة");
    document.getElementById("summaryAssociated").textContent=val(r.associated_symptoms,"لا توجد معلومات محددة");
    document.getElementById("summaryDanger").textContent=val(r.danger_status,"لم يتم رصد علامات خطر واضحة");
    document.getElementById("summaryPriority").textContent=`${val(r.severity)} / ${val(r.priority)}`;
    document.getElementById("summaryPath").textContent=val(r.path);

    document.getElementById("docAgeGender").textContent=val(r.age_gender);
    document.getElementById("docDuration").textContent=val(r.duration,"غير محددة");
    document.getElementById("docSymptoms").textContent=val(r.detected_symptoms);
    document.getElementById("docAssociated").textContent=val(r.associated_symptoms,"لا توجد معلومات محددة");
    document.getElementById("docDanger").textContent=val(r.danger_status);
    document.getElementById("docPriority").textContent=`${val(r.severity)} / ${val(r.priority)}`;
    document.getElementById("docPath").textContent=val(r.path);
    document.getElementById("doctorSummaryText").textContent=val(r.doctor_summary,"تم تنظيم المعلومات من وصف المريض.");
    const notice=document.getElementById("noticeBox");
    notice.classList.toggle("danger",Array.isArray(r.danger_signs)&&r.danger_signs.length>0);
}

function openModal(type){
    document.getElementById("modal").classList.add("show");
    document.getElementById("modalTitle").textContent=type==="nearest"?"أقرب موعد":"حجز موعد";
    document.getElementById("modalText").textContent=type==="nearest"?"أقرب موعد مقترح حسب المواعيد المتاحة.":"اختر الموعد المناسب لك.";
}
function closeModal(){document.getElementById("modal").classList.remove("show")}
function confirmAppointment(){closeModal();alert("تم تأكيد الموعد بنجاح");}

async function loadDashboard(){
    try{
        const r=await fetch("/patterns");
        if(!r.ok) return;
        const data=await r.json();
        document.getElementById("kpiTotal").textContent=data.total_cases||0;
        document.getElementById("kpiRecent").textContent=data.recent_cases||0;
        document.getElementById("kpiAlerts").textContent=(data.alerts||[]).length;
        const alertBox=document.getElementById("patternAlert");
        if((data.alerts||[]).length){
            const a=data.alerts[0];
            alertBox.querySelector("b").textContent="لوحظ ارتفاع في الحالات";
            alertBox.querySelector("p").textContent=`${a.message} خلال الفترة الأخيرة مقارنة بالفترة السابقة.`;
        }else{
            alertBox.querySelector("b").textContent="لا توجد تنبيهات حالية";
            alertBox.querySelector("p").textContent="لم يتم رصد نمط متزايد وفق البيانات المسجلة.";
        }
    }catch(e){}
}

document.addEventListener("DOMContentLoaded",loadDashboard);
