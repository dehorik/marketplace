function getAdmins(adminsGrid) {
    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/users",
                method: "get",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then((response) => {
                    for (let admin of response.data.users) {
                        appendAdmin(admin, adminsGrid);
                    }
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}

function appendAdmin(admin, adminsGrid) {
    adminsGrid.append(createAdminNode(admin));
}

function createAdminNode(admin) {
    const container = document.createElement("div");
    container.className = "admin-container";

    const node = document.createElement("div");
    node.className = "admin";
    node.setAttribute("data-user_id", admin.user_id);
    container.appendChild(node);

    const photoContainer = document.createElement("div");
    const photo = document.createElement("img");
    photoContainer.className = "admin-photo-container";
    if (admin.has_photo) {
        photo.src = `/images/users/${admin.user_id}.jpg?reload=${Date.now()}`;
    }
    else {
        photo.src = "/static/img/default-avatar.png"
    }
    photoContainer.appendChild(photo);
    node.appendChild(photoContainer);

    const textDataContainer = document.createElement("div");
    const textData = document.createElement("div");
    const nameContainer = document.createElement("div");
    const roleContainer = document.createElement("div");
    const name = document.createElement("span");
    const role = document.createElement("span");
    textDataContainer.className =  "admin-text-data-container";
    textData.className = "admin-text-data";
    nameContainer.className = "admin-name-container";
    roleContainer.className = "admin-role-container";
    roleContainer.setAttribute("data-role_id", admin.role_id);
    name.textContent = admin.username;
    role.textContent = admin.role_name;
    nameContainer.appendChild(name);
    roleContainer.appendChild(role);
    textData.appendChild(nameContainer);
    textData.appendChild(roleContainer);
    textDataContainer.appendChild(textData);
    node.appendChild(textDataContainer);

    if (admin.user_id !== decodeToken(getToken()).sub) {
        const buttonsContainer = document.createElement("div");
        const buttons = document.createElement("div");
        const editingButton = document.createElement("a");
        const deleteButton = document.createElement("a");
        const editingButtonText = document.createElement("span");
        const deleteButtonText = document.createElement("span");
        buttonsContainer.className = "admin-buttons-container";
        buttons.className = "admin-buttons";
        editingButtonText.textContent = "Изменить роль";
        deleteButtonText.textContent = "Удалить администратора";
        editingButton.appendChild(editingButtonText);
        deleteButton.appendChild(deleteButtonText);
        buttons.appendChild(editingButton);
        buttons.appendChild(deleteButton);
        buttonsContainer.appendChild(buttons);

        node.appendChild(buttonsContainer);

        const editingFormContainer = document.createElement("div");
        editingFormContainer.classList.add("admin-editing-form-container", "no-display");

        const editingForm = document.createElement("form");

        const returnButtonContainer = document.createElement("div");
        const returnButton = document.createElement("a");
        const returnButtonText = document.createElement("span");
        returnButtonContainer.className = "admin-editing-form-return-btn-container";
        returnButtonText.textContent = "Вернуться назад";
        returnButton.appendChild(returnButtonText);
        returnButtonContainer.appendChild(returnButton);

        const editingFormButtonsContainer = document.createElement("div");
        editingFormButtonsContainer.className = "admin-editing-form-buttons-container";

        const userButtonContainer = document.createElement("div");
        const userButton = document.createElement("input");
        const userLabel = document.createElement("label");
        const userLabelText = document.createElement("span");
        userButton.type = "radio";
        userButton.name = "role_id";
        userButton.value = "1";
        userButton.id = "admin-editing-form-user-btn";
        userLabel.htmlFor = "admin-editing-form-user-btn";
        userLabelText.textContent = "Пользователь";
        userLabel.appendChild(userLabelText);
        userButtonContainer.append(userLabel, userButton);

        const adminButtonContainer = document.createElement("div");
        const adminButton = document.createElement("input");
        const adminLabel = document.createElement("label");
        const adminLabelText = document.createElement("span");
        adminButton.type = "radio";
        adminButton.name = "role_id";
        adminButton.value = "2";
        adminButton.id = "admin-editing-form-admin-btn";
        adminLabel.htmlFor = "admin-editing-form-admin-btn";
        adminLabelText.textContent = "Администратор";
        adminLabel.appendChild(adminLabelText);
        adminButtonContainer.append(adminLabel, adminButton);

        const superuserButtonContainer = document.createElement("div");
        const superuserButton = document.createElement("input");
        const superuserLabel = document.createElement("label");
        const superuserLabelText = document.createElement("span");
        superuserButton.type = "radio";
        superuserButton.name = "role_id";
        superuserButton.value = "3";
        superuserButton.id = "admin-editing-form-superuser-btn";
        superuserLabel.htmlFor = "admin-editing-form-superuser-btn";
        superuserLabelText.textContent = "Суперпользователь";
        superuserLabel.appendChild(superuserLabelText);
        superuserButtonContainer.append(superuserLabel, superuserButton);

        switch (Number(roleContainer.getAttribute("data-role_id"))) {
            case 1:
                userButton.checked = true;
                break;
            case 2:
                adminButton.checked = true;
                break;
            case 3:
                superuserButton.checked = true;
                break;
        }

        editingFormButtonsContainer.appendChild(userButtonContainer);
        editingFormButtonsContainer.appendChild(adminButtonContainer);
        editingFormButtonsContainer.appendChild(superuserButtonContainer);

        const submitButtonContainer = document.createElement("div");
        const submitButton = document.createElement("button");
        submitButtonContainer.className = "admin-editing-form-submit-btn-container";
        submitButton.type = "submit";
        submitButton.textContent = "Сохранить";
        submitButtonContainer.append(submitButton);

        editingForm.appendChild(returnButtonContainer);
        editingForm.appendChild(editingFormButtonsContainer);
        editingForm.appendChild(submitButtonContainer);

        editingFormContainer.appendChild(editingForm);
        node.appendChild(editingFormContainer);

        deleteButton.addEventListener("click", () => {
            deleteAdmin(admin.username, container);
        });

        editingButton.addEventListener("click", () => {
            photoContainer.classList.add("no-display");
            textDataContainer.classList.add("no-display");
            buttonsContainer.classList.add("no-display");

            userButton.checked = false;
            adminButton.checked = false;
            superuserButton.checked = false;

            switch (Number(roleContainer.getAttribute("data-role_id"))) {
                case 1:
                    userButton.checked = true;
                    break;
                case 2:
                    adminButton.checked = true;
                    break;
                case 3:
                    superuserButton.checked = true;
                    break;
            }

            editingFormContainer.classList.remove("no-display");
        });

        returnButton.addEventListener("click", () => {
            editingFormContainer.classList.add("no-display");

            userButton.checked = false;
            adminButton.checked = false;
            superuserButton.checked = false;

            switch (admin.role_id) {
                case 1:
                    userButton.checked = true;
                    break;
                case 2:
                    adminButton.checked = true;
                    break;
                case 3:
                    superuserButton.checked = true;
                    break;
            }

            photoContainer.classList.remove("no-display");
            textDataContainer.classList.remove("no-display");
            buttonsContainer.classList.remove("no-display");
        });


        editingForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const currentRoleId = Number(roleContainer.getAttribute("data-role_id"));
            const newRoleId = Number(editingFormButtonsContainer.querySelector("input[name='role_id']:checked").value);

            if (currentRoleId === newRoleId) {
                returnButton.click();
            }
            else {
                updateAdmin(admin.username, newRoleId, container);
            }
        });
    }

    return container;
}
