const login_by_email_btn = document.getElementById("login-by-email-btn");
const login_method_label = document.querySelector("#username-input-container label");
const form = document.querySelector("#registration-form-container form");


login_by_email_btn.addEventListener("click", () => {
    if (login_method_label.innerHTML === "Имя пользователя") {
        login_method_label.innerHTML = "Почта";
        login_by_email_btn.value = "Войти по имени";

        input_username_elem.name = "user_email";
    }
    else {
        login_method_label.innerHTML = "Имя пользователя";
        login_by_email_btn.value = "Войти по почте";

        input_username_elem.name = "user_name";
    }
});

form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (input_username_elem.value.length > 16 && !(input_username_elem.name === "user_email")) {
        return;
    }
    else if (input_username_elem.value.length > 32 && input_username_elem.name === "user_email") {
        return;
    }
    else if (input_username_elem.value.length < 6) {
        return;
    }

    if (input_password_elem.value.length > 18) {
        return;
    }
    else if (input_password_elem.value.length < 8) {
        return;
    }

    const form_data = new FormData(form);

    axios.post("/auth/login", form_data)
        .then(function (response) {
            successful_auth(response);
        });
});

