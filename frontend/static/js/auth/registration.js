function registration(username, password) {
    const data = new FormData();

    data.append("username", username);
    data.append("password", password);

    axios({
        url: "/auth/registration",
        method: "post",
        data: data
    })
        .then((response) => {
            console.log(response.data);
        })
        .catch((response) => {
            if (response.status === 409) {
                username_error.textContent = "Имя пользователя уже занято";
            }
            else {
                username_error.textContent = "Ошибка регистрации";
                password_error.textContent = "Ошибка регистрации";
            }
        });
}