function updateAdmin(username, roleId, container) {
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
                .then(() => {
                    switch (roleId) {
                        case 1:
                            container.classList.add("deleted-admin-container");
                            container.firstChild.innerHTML = null;
                            container.firstChild.classList.add("deleted-admin");

                            setTimeout(() => {
                                container.remove();
                            }, 1050);

                            break;
                        case 2:
                            container.querySelector(".admin-role-container").setAttribute("data-role_id", String(2));
                            container.querySelector(".admin-role-container span").textContent = "Администратор";
                            container.querySelector(".admin-editing-form-return-btn-container a").click();

                            break
                        case 3:
                            container.querySelector(".admin-role-container").setAttribute("data-role_id", String(3));
                            container.querySelector(".admin-role-container span").textContent = "Суперпользователь";
                            container.querySelector(".admin-editing-form-return-btn-container a").click();

                            break
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