function updateUser(form, old_user_data) {
    const form_photo = document.querySelector(".user-data-editing-form_photo-container img");
    const form_photo_status = form_photo.getAttribute("data-photo-type");

    const form_data = new FormData(form);
    const username = form_data.get("username");
    const password = form_data.get("password");
    const email = form_data.get("email");
    const photo = form_data.get("photo");

    const data = new FormData();

    if (form_photo_status === "default" && old_user_data.photo_path) {
        data.set("clear_photo", "true");
    }
    else {
        data.set("clear_photo", "false");
    }

    if (!email && old_user_data.email) {
        data.set("clear_email", "true");
    }
    else {
        data.set("clear_email", "false");
    }

    if (username !== old_user_data.username) {
        data.set("username", username);
    }

    if (password) {
        data.set("password", password);
    }

    if (email && email !== old_user_data.email) {
        data.set("email", email);
    }

    if (photo && photo.size > 0) {
        data.set("photo", photo);
    }

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
                    const global_error = document.querySelector(".user-data-editing-form_error span");

                    if (error.status === 401 || error.status === 404) {
                        deleteToken();
                        window.location.href = "/auth/form";
                    }
                    else if (error.status === 415) {
                        global_error.textContent = "Невалидный файл";
                    }
                    else if (error.status === 409) {
                        global_error.textContent = "Юзернейм уже занят";
                    }
                    else {
                        global_error.textContent = "Ошибка в введённых данных";
                    }
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}
