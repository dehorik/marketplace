function createAdmin(username, roleId, container) {
    // запрос на добавление администратора (суперпользователя)

    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/users/roles",
                method: "patch",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: {
                    username: username,
                    role_id: roleId
                }
            })
                .then((response) => {
                    container.parentNode.replaceChild(createAdminNode(response.data), container);
                })
                .catch(() => {
                    const errorText = container.querySelector(".admin-creation-form-username-error-container span");
                    errorText.textContent = "Не удалось добавить администратора";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}
