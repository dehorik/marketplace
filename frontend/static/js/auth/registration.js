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
            setToken(response.data.token.access_token);
            window.location.href = "/users/me/home";
            createCartItems();
        })
        .catch((error) => {
            if (error.status === 409) {
                global_error_message.textContent = "Имя пользователя уже занято!";
            }
            else {
                global_error_message.textContent = "Ошибка аутентификации";
            }
        });
}