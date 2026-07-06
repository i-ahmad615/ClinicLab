document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-confirm]").forEach((btn) => {
        btn.addEventListener("click", (event) => {
            const message = btn.getAttribute("data-confirm");
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

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

    const reasonChoice = document.querySelector("#reasonChoice");
    const reasonOther = document.querySelector("#reasonOther");
    if (reasonChoice && reasonOther) {
        const toggleReason = () => {
            if (reasonChoice.value === "Other") {
                reasonOther.classList.remove("d-none");
                reasonOther.required = true;
            } else {
                reasonOther.classList.add("d-none");
                reasonOther.required = false;
                reasonOther.value = "";
            }
        };
        reasonChoice.addEventListener("change", toggleReason);
        toggleReason();
    }
});
