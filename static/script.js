async function analyzeSymptoms() {

    const text = document
        .getElementById("symptoms")
        .value
        .trim();

    const resultBox =
        document.getElementById("result");


    if (!text) {

        resultBox.classList.remove("hidden");

        resultBox.innerHTML = `
            <div class="summary">
                الرجاء كتابة الأعراض أولًا.
            </div>
        `;

        return;
    }


    resultBox.classList.remove("hidden");

    resultBox.innerHTML = `
        <div class="summary">
            جارٍ تحليل الأعراض...
        </div>
    `;


    try {

        const response = await fetch(
            "/analyze",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    text: text
                })
            }
        );


        const data =
            await response.json();


        let symptoms =
            data.detected_symptoms.length
                ? data.detected_symptoms.join("، ")
                : "لم يتم التعرف على أعراض محددة";


        let priorityText =
            "منخفضة";


        if (data.priority === "medium") {

            priorityText = "متوسطة";

        }


        if (data.priority === "high") {

            priorityText = "عالية";

        }


        // إذا كانت الحالة عالية الأولوية
        if (data.priority === "high") {

            resultBox.innerHTML = `

                <h3 class="result-title">
                    نتيجة التقييم الأولي
                </h3>

                <div class="result-grid">

                    <div class="result-item">

                        <span>
                            الأعراض المرصودة
                        </span>

                        <strong>
                            ${symptoms}
                        </strong>

                    </div>


                    <div class="result-item">

                        <span>
                            شدة الأعراض
                        </span>

                        <strong>
                            ${data.severity}
                        </strong>

                    </div>


                    <div class="result-item">

                        <span>
                            الأولوية
                        </span>

                        <strong>
                            عالية
                        </strong>

                    </div>

                </div>


                <div class="summary">

                    🚨
                    <strong>
                        يُنصح بالتوجه للرعاية العاجلة.
                    </strong>

                    <br>

                    هذه النتيجة للتوجيه الأولي
                    ولا تُعد تشخيصًا طبيًا.

                </div>

            `;

            return;
        }


        // الحالات العادية
        resultBox.innerHTML = `

            <h3 class="result-title">
                نتيجة التقييم الأولي
            </h3>


            <div class="result-grid">


                <div class="result-item">

                    <span>
                        الأعراض المرصودة
                    </span>

                    <strong>
                        ${symptoms}
                    </strong>

                </div>


                <div class="result-item">

                    <span>
                        مدة الأعراض
                    </span>

                    <strong>
                        ${data.duration}
                    </strong>

                </div>


                <div class="result-item">

                    <span>
                        شدة الأعراض
                    </span>

                    <strong>
                        ${data.severity}
                    </strong>

                </div>


            </div>


            <div class="summary">

                ${data.doctor_summary}

                <br><br>

                <button
                    class="primary-button"
                    onclick="showAppointment()"
                >
                    حجز موعد
                </button>

            </div>

        `;


    } catch (error) {

        resultBox.innerHTML = `

            <div class="summary">

                حدث خطأ أثناء الاتصال بالنظام.

                <br>

                تأكدي من تشغيل السيرفر.

            </div>

        `;

        console.error(error);
    }
}


/* ================= MODALS ================= */


function showAppointment() {

    document
        .getElementById("modalIcon")
        .innerHTML = "📅";


    document
        .getElementById("modalTitle")
        .innerText = "حجز موعد";


    document
        .getElementById("modalText")
        .innerText =
        "أقرب موعد متاح في المركز الصحي";


    document
        .getElementById("modal")
        .classList.remove("hidden");
}



function showNearest() {

    document
        .getElementById("modalIcon")
        .innerHTML = "🕐";


    document
        .getElementById("modalTitle")
        .innerText = "أقرب موعد";


    document
        .getElementById("modalText")
        .innerText =
        "تم العثور على أقرب موعد متاح لك";


    document
        .getElementById("modal")
        .classList.remove("hidden");
}



function showEmergency() {

    document
        .getElementById("modalIcon")
        .innerHTML = "🚨";


    document
        .getElementById("modalTitle")
        .innerText =
        "التوجه للطوارئ";


    document
        .getElementById("modalText")
        .innerText =
        "إذا كانت الأعراض شديدة أو طارئة، يرجى طلب الرعاية العاجلة فورًا.";


    document
        .getElementById("modal")
        .classList.remove("hidden");
}



function closeModal() {

    document
        .getElementById("modal")
        .classList.add("hidden");
}



function confirmAppointment() {

    document
        .getElementById("modalText")
        .innerText =
        "تم تأكيد الموعد التجريبي بنجاح.";


    document
        .querySelector(".appointment-option")
        .style.display = "none";


    document
        .querySelector(".modal-content .primary-button")
        .innerText = "تم التأكيد ✓";
}
