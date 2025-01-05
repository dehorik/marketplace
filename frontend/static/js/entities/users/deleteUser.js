function deleteUser() {
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
                    const error_node = document.querySelector(".user-deletion-form_error span");

                    if (error.status === 401 || error.status === 404) {
                        deleteToken();
                        window.location.href = "/";
                    }
                    else if (error.status === 409) {
                        error_node.textContent = "Удаление не удалось: требуется как минимум 1 суперюзер";
                    }
                    else {
                        error_node.textContent = "Удаление не удалось: возникли ошибки во время процесса";
                    }
                });
        })
        .catch(() => {
           deleteToken();
           window.location.href = "/auth/form";
        });
}
