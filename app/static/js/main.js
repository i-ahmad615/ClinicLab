document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-confirm]").forEach((btn) => {
        btn.addEventListener("click", (event) => {
            const message = btn.getAttribute("data-confirm");
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    const dobInput = document.querySelector("#dob");
    const ageInput = document.querySelector("#age");
    if (dobInput && ageInput) {
        dobInput.addEventListener("change", () => {
            const dob = new Date(dobInput.value);
            if (Number.isNaN(dob.getTime())) {
                ageInput.value = "";
                return;
            }
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const monthDiff = today.getMonth() - dob.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                age -= 1;
            }
            ageInput.value = age;
        });
    }

    const patientSearch = document.querySelector("#patientSearch");
    const patientSelect = document.querySelector("#patientSelect");
    if (patientSearch && patientSelect) {
        patientSearch.addEventListener("input", () => {
            const query = patientSearch.value.toLowerCase();
            const options = Array.from(patientSelect.options);
            options.forEach((option) => {
                if (!option.value) {
                    option.hidden = false;
                    return;
                }
                const text = option.text.toLowerCase();
                option.hidden = query && !text.includes(query);
            });
        });
    }
});
