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
                global_error_message.textContent = "Имя пользователя уже занято!";
            }
            else {
                global_error_message.textContent = "Ошибка аутентификации";
            }
        });
}