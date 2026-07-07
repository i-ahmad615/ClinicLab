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

    const loginPassword = document.querySelector("#loginPassword");
    const toggleLoginPassword = document.querySelector("#toggleLoginPassword");
    const toggleLoginPasswordIcon = document.querySelector("#toggleLoginPasswordIcon");
    if (loginPassword && toggleLoginPassword && toggleLoginPasswordIcon) {
        const eyeIcon = `
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            </svg>`;
        const eyeOffIcon = `
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C5 20 1 12 1 12a21.6 21.6 0 0 1 5.06-6.94"></path>
                <path d="M10.58 10.58A3 3 0 1 0 13.42 13.42"></path>
                <path d="M1 1l22 22"></path>
                <path d="M9.88 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a21.67 21.67 0 0 1-2.92 4.31"></path>
            </svg>`;

        toggleLoginPassword.addEventListener("click", () => {
            const isPassword = loginPassword.type === "password";
            loginPassword.type = isPassword ? "text" : "password";
            toggleLoginPassword.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
            toggleLoginPasswordIcon.innerHTML = isPassword ? eyeOffIcon : eyeIcon;
        });
    }
});
