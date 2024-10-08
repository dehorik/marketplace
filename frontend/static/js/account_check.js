window.addEventListener("load", account_check);


function account_check() {
    const container = document.querySelector(".account");

    try {
        refresh_tokens();

        axios.get(
            "/users/me/data", {
                headers: {
                    Authorization: `Bearer ${get_token()}`
                }
            })
            .then(function (response) {
                const profile = document.createElement('div');
                profile.className = "user-profile";

                const profile_photo = document.createElement('img');

                if (response.data.photo_path) {
                    profile_photo.src = response.data.photo_path;
                }
                else {
                    profile_photo.src = "/static/img/default_avatar.png";
                }

                profile.append(profile_photo);
                container.append(profile);
            });
    }
    catch (error) {
        if (error instanceof AuthenticationError) {
            const auth_buttons = document.createElement("div");
            auth_buttons.className = "auth-buttons";

            const registration_button = document.createElement("a");
            registration_button.href = '/auth/registration';
            registration_button.innerHTML = "Регистрация";

            const login_button = document.createElement("a");
            login_button.href = '/auth/login';
            login_button.innerHTML = "Вход";

            auth_buttons.append(registration_button);
            auth_buttons.append(login_button);
            container.append(auth_buttons);
        }
    }
}
