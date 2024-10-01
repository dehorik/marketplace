window.addEventListener("load", load_user_photo);


function load_user_photo() {
    const container_elem = document.querySelector(".user__manager");
    const access_token = get_token();

    if (access_token) {
        verify_token();

        axios.get(
            "/users/me/data", {
                headers: {
                    Authorization: `Bearer ${access_token}`
                }
            })
            .then(function (response) {
                const profile_elem = document.createElement('div');
                profile_elem.className = "user__profile";
                const profile_elem_photo = document.createElement('img');

                const user_photo_path = response.data.user_photo_path;

                if (user_photo_path) {
                    profile_elem_photo.src = user_photo_path;
                }
                else {
                    profile_elem_photo.src = "/static/img/default_avatar.png";
                }

                profile_elem.append(profile_elem_photo);
                container_elem.append(profile_elem);
            });
    }
    else {
        const auth_elem = document.createElement("div");
        auth_elem.className = "auth__elem";
        const registration_elem = document.createElement("a");
        const login_elem = document.createElement("a");

        registration_elem.href = '/auth/registration';
        login_elem.href = '/auth/login';
        registration_elem.innerHTML = "Регистрация";
        login_elem.innerHTML = "Вход";

        auth_elem.append(registration_elem);
        auth_elem.append(login_elem);
        container_elem.append(auth_elem);
    }
}
