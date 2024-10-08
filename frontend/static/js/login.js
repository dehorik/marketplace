const form = document.querySelector(".elements-container form");


form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!validate_form_data()) {
        return;
    }

    const form_data = new FormData(form);

    axios.post("/auth/login", form_data)
        .then(function (response) {
            const user = response.data.user;
            const access_token = response.data.token.access_token;

            set_token(access_token);
            localStorage.setItem("user_id", user.user_id);

            welcome_user(user.username);
        })
        .catch(function (error) {
           if (error.response.status === 403) {
               invalid_username_msg.innerHTML = "Некорректное имя пользователя или пароль";
               invalid_password_msg.innerHTML = "Некорректное имя пользователя или пароль";
           }
           else if (error.response.status === 422) {
               invalid_username_msg.innerHTML = "Невалидные данные";
               invalid_password_msg.innerHTML = "Невалидные данные";
           }
        });
});
