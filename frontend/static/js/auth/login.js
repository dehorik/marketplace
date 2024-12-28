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
                username_error.textContent = "Пользователь не найден";
            }
            else {
                username_error.textContent = "Ошибка входа в аккаунт";
                password_error.textContent = "Ошибка входа в аккаунт";
            }
        });
}
