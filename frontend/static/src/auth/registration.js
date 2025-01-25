function registration(username, password) {
    axios({
        url: "/auth/registration",
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

            if (error.status === 409) {
                errorText.textContent = "Имя пользователя уже занято";
            }
            else {
                errorText.textContent = "Ошибка регистрации";
            }
        });
}