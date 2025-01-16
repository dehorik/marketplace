function login(username, password) {
    const data = new FormData();

    data.append("username", username);
    data.append("password", password);

    axios({
        url: "/auth/login",
        method: "post",
        data: data
    })
        .then((response) => {
            setToken(response.data.token.access_token);

            const url = new URL(window.location.href);
            window.location.href = url.searchParams.get('redirect_url');

            createCartItems();
        })
        .catch((error) => {
            if (error.status === 401) {
                global_error_message.textContent = "Неверное имя пользователя или пароль!";
            }
            else {
                global_error_message.textContent = "Ошибка аутентификации";
            }
        });
}
