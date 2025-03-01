function deleteAdmin(username, container) {
    // запрос на удаление админа (установка минимально возможной роли)

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
                    role_id: 1
                }
            })
                .then(() => {
                    container.classList.add("deleted-admin-container");
                    container.firstChild.innerHTML = null;
                    container.firstChild.classList.add("deleted-admin");

                    setTimeout(() => {
                        container.remove();
                    }, 1050);
                })
                .catch(() => {
                    const errorContainer = document.createElement("div");
                    const error = document.createElement("span");
                    errorContainer.className = "admin-error-container";
                    error.textContent = "Не удалось удалить администратора";
                    errorContainer.appendChild(error);

                    container.firstChild.innerHTML = null;
                    container.firstChild.appendChild(errorContainer);
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}
