function login(username, password) {
    axios({
        url: "/auth/login",
        method: "post",
        data: {
            username: username,
            password: password
        }
    })
        .then((response) => {
            setToken(response.data.token.access_token);
            window.location.href = new URL(window.location.href).searchParams.get('redirect_url');
            createCartItems();
        })
        .catch((error) => {
            const errorText = document.querySelector(".auth-form_error-message span");

            if (error.status === 401) {
                errorText.textContent = "Неверное имя пользователя или пароль";
            }
            else {
                errorText.textContent = "Ошибка входа в аккаунт";
            }
        });
}
