function deleteUser() {
    // апи запрос на удаление пользователя

    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/users/me",
                method: "delete",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then(() => {
                    deleteToken();
                    window.location.href = "/";
                })
                .catch((error) => {
                    const errorText = document.querySelector(".user-deletion-form_error span");

                    if (error.status === 409) {
                        errorText.textContent = "Удаление не удалось: требуется как минимум 1 суперюзер";
                    }
                    else {
                        errorText.textContent = "Удаление не удалось: возникли ошибки во время процесса";
                    }
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}
