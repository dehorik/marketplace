function appendAdminCreationForm(adminsGrid) {
    // добавление формы для создания админа (выдачи прав пользователю);
    // форма добавляется непосредственно в сетку админов

    if (!adminsGrid.querySelector(".admin-creation-form")) {
        adminsGrid.prepend(getAdminCreationForm(adminsGrid));
    }
}

function deleteAdminCreationForm(container) {
    // удаление формы для создания админа

    container.classList.add("deleted-admin-container");
    container.firstChild.innerHTML = null;
    container.firstChild.classList.add("deleted-admin");

    setTimeout(() => {
        container.remove();
    }, 1050);
}

function getAdminCreationForm(adminsGrid) {
    // создание дом узла формы для создания админа;
    // все нужные обработчики вешаются тут же

    const container = document.createElement("div");
    container.className = "admin-container";

    const node = document.createElement("div");
    node.className = "admin";

    const form = document.createElement("form");
    form.className = "admin-creation-form";
    form.autocomplete = "off";

    const usernameContainer = document.createElement("div");
    const usernameInputLabel = document.createElement("label");
    const usernameInput = document.createElement("input");
    const formErrorContainer = document.createElement("div");
    const formErrorText = document.createElement("span");
    usernameContainer.className = "admin-creation-form-username-container";
    usernameInputLabel.htmlFor = "admin-creation-form-username";
    usernameInput.id = "admin-creation-form-username";
    usernameInput.type = "text";
    usernameInput.placeholder = "Юзернейм";
    formErrorContainer.className = "admin-creation-form-username-error-container";
    formErrorContainer.appendChild(formErrorText);
    usernameContainer.append(usernameInputLabel, usernameInput, formErrorContainer);

    const roleButtonsContainer = document.createElement("div");
    roleButtonsContainer.className = "admin-creation-form-role-buttons";

    const adminButtonContainer = document.createElement("div");
    const adminButtonLabel = document.createElement("label");
    const adminButtonLabelText = document.createElement("span");
    const adminButton = document.createElement("input");
    adminButtonLabel.htmlFor = "admin-creation-form-admin-btn";
    adminButtonLabelText.textContent = "Администратор";
    adminButton.id = "admin-creation-form-admin-btn";
    adminButton.type = "radio";
    adminButton.name = "role_id";
    adminButton.checked = true;
    adminButton.value = "2";
    adminButtonLabel.appendChild(adminButtonLabelText);
    adminButtonContainer.append(adminButtonLabel, adminButton);

    const superuserButtonContainer = document.createElement("div");
    const superuserButtonLabel = document.createElement("label");
    const superuserButtonLabelText = document.createElement("span");
    const superuserButton = document.createElement("input");
    superuserButtonLabel.htmlFor = "admin-creation-form-superuser-btn";
    superuserButtonLabelText.textContent = "Суперпользователь";
    superuserButton.id = "admin-creation-form-superuser-btn";
    superuserButton.type = "radio";
    superuserButton.name = "role_id";
    superuserButton.value = "3";
    superuserButtonLabel.appendChild(superuserButtonLabelText);
    superuserButtonContainer.append(superuserButtonLabel, superuserButton);

    roleButtonsContainer.appendChild(adminButtonContainer);
    roleButtonsContainer.appendChild(superuserButtonContainer);

    const submitButtonsContainer = document.createElement("div");
    submitButtonsContainer.className = "admin-creation-form-buttons";

    const submitButton = document.createElement("button");
    submitButton.type = "submit";
    submitButton.textContent = "Добавить";

    const cancelButtonContainer = document.createElement("div");
    const cancelButton = document.createElement("a");
    const cancelButtonText = document.createElement("span");
    cancelButtonText.textContent = "Отменить";
    cancelButton.appendChild(cancelButtonText);
    cancelButtonContainer.appendChild(cancelButton);

    submitButtonsContainer.appendChild(submitButton);
    submitButtonsContainer.appendChild(cancelButtonContainer);

    form.append(usernameContainer, roleButtonsContainer, submitButtonsContainer);
    node.appendChild(form);
    container.appendChild(node);

    usernameInput.addEventListener("input", (event) => {
        checkAdminUsername(event.target.value.trim(), formErrorText);
    });

    cancelButton.addEventListener("click", () => {
        deleteAdminCreationForm(container);
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!checkAdminUsername(usernameInput.value.trim(), formErrorText)) return;

        const username = usernameInput.value.trim();
        const roleId = container.querySelector("input[name='role_id']:checked").value;

        for (let node of adminsGrid.children) {
            const adminUsernameNode = node.querySelector(".admin-name-container span");

            if (adminUsernameNode && adminUsernameNode.textContent === username) {
                formErrorText.textContent = "Такой администратор уже существует";

                return;
            }
        }

        createAdmin(username, roleId, container);
    });

    return container
}

function checkAdminUsername(username, errorText) {
    // валидация юзернейма

    if (username.length === 0) {
        errorText.textContent = null;
    }
    else if (username.length < 6 || username.length > 16) {
        errorText.textContent = "Невалидное имя пользователя";
    }
    else {
        errorText.textContent = null;
        return true;
    }
}
