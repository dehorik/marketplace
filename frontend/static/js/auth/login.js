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
            console.log(response.data);
        })
        .catch((response) => {
            if (response.status === 401) {
                global_error_message.textContent = "Неверное имя пользователя или пароль!";
            }
            else {
                global_error_message.textContent = "Ошибка аутентификации";
            }
        });
}
