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

            const url = new URL(window.location.href);
            window.location.href = url.searchParams.get('redirect_url');

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