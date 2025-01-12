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
            window.location.href = "/users/me/home";
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
