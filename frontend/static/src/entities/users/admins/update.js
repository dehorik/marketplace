function updateAdmin(username, roleId, container) {
    // запрос на обновление роли админа

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
                    if (Number(response.data.role_id) === 1) {
                        // если роль сменилась на минимально возможную - аккаунт больше не имеет прав админа

                        container.classList.add("deleted-admin-container");
                        container.firstChild.innerHTML = null;
                        container.firstChild.classList.add("deleted-admin");

                        setTimeout(() => {
                            container.remove();
                        }, 1050);
                    }
                    else {
                        container.querySelector(".admin-role-container").setAttribute("data-role_id", response.data.role_id);
                        container.querySelector(".admin-role-container span").textContent = response.data.role_name;
                        container.querySelector(".admin-editing-form-return-btn-container a").click();
                    }
                })
                .catch(() => {
                    const errorContainer = document.createElement("div");
                    const error = document.createElement("span");
                    errorContainer.className = "admin-error-container";
                    error.textContent = "Не удалось обновить роль";
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