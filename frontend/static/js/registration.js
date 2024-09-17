const form = document.querySelector("#registration-form-container form");


form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!validate_form_data()) {
        return;
    }

    const form_data = new FormData(form);

    axios.post("/auth/registration", form_data)
        .then(function (response) {
            const user = response.data.user;
            const access_token = response.data.token.access_token;
            set_token(access_token);

            get_message(user, '/products/list');
        })
        .catch(function (error) {
            if (error.response.status === 409) {
                invalid_username_msg.innerHTML = "Имя пользователя уже занято!";
            }

            else if (error.response.status === 422) {
                invalid_username_msg.innerHTML = "Невалидные данные";
                invalid_password_msg.innerHTML = "Невалидные данные";
            }
        });
});