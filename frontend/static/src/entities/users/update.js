function updateUser(clearEmail, clearPhoto, username, password, email, photo) {
    const data = new FormData();

    data.set("clear_email", clearEmail);
    data.set("clear_photo", clearPhoto);

    if (username) data.set("username", username);
    if (password) data.set("password", password);
    if (email) data.set("email", email);
    if (photo) data.set("photo", photo);

    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/users/me",
                method: "patch",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: data
            })
                .then((response) => {
                    appendUserPage(response.data);
                })
                .catch((error) => {
                    const errorText = document.querySelector(".user-data-editing-form_error span");

                    if (error.status === 409) {
                        errorText.textContent = "Юзернейм уже занят";
                    }
                    else {
                        errorText.textContent = "Ошибка обновления данных";
                    }
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}
