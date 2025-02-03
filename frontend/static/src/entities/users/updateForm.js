function appendUserUpdateForm(user) {
    const container = document.querySelector(".user-page_container");

    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    container.appendChild(getUserUpdateForm(user));
}

function getUserUpdateForm(user) {
    const container = document.createElement("div");
    container.className = "user-data-editing-form";

    const title = document.createElement("div");
    title.className = "user-data-editing-form_title";

    const titleReturnBtn = document.createElement("div");
    const returnBtnImg = document.createElement("img");
    titleReturnBtn.className = "user-data-editing-form_title-return-btn";
    returnBtnImg.src = "/static/img/back.png";
    returnBtnImg.alt = "back";
    titleReturnBtn.appendChild(returnBtnImg);
    const titleTextContainer = document.createElement("div");
    const titleText = document.createElement("span");
    titleTextContainer.className = "user-data-editing-form_title-text";
    titleText.textContent = "Изменение данных пользователя";
    titleTextContainer.appendChild(titleText);

    title.appendChild(titleReturnBtn);
    title.appendChild(titleTextContainer);

    const form = document.createElement("form");
    form.autocomplete = "off";

    const photoManagement = document.createElement("div");
    photoManagement.className = "user-data-editing-form_photo-management";

    const photoContainer = document.createElement("div");
    photoContainer.className = "user-data-editing-form_photo-container";
    const photo = document.createElement("img");
    photo.alt = "user";

    if (user.has_photo) {
        photo.src = `/images/users/${user.user_id}.jpg?reload=${Date.now()}`;
        photo.setAttribute("data-photo-type", "uploaded");
    }
    else {
        photo.src = "/static/img/default-avatar.png";
        photo.setAttribute("data-photo-type", "default");
    }

    photoContainer.appendChild(photo);

    const photoButtonsContainer = document.createElement("div");
    photoButtonsContainer.className = "user-data-editing-form_photo-buttons-container";
    const photoButtons = document.createElement("div");
    photoButtons.className = "user-data-editing-form_photo-buttons";

    const photoUploadBtn = document.createElement("div");
    const photoUploadBtnText = document.createElement("span");
    const fileInput = document.createElement("input");
    photoUploadBtnText.textContent = "Загрузить фото";
    fileInput.id = "input-user-photo";
    fileInput.name = "photo";
    fileInput.className = "no-display";
    fileInput.type = "file";
    fileInput.accept = ".jpg, .png";
    photoUploadBtn.appendChild(photoUploadBtnText);
    photoUploadBtn.appendChild(fileInput);

    const photoDeleteBtn = document.createElement("div");
    const photoDeleteBtnText = document.createElement("span");
    photoDeleteBtnText.textContent = "Удалить фото";
    photoDeleteBtn.appendChild(photoDeleteBtnText);

    photoButtons.appendChild(photoUploadBtn);
    photoButtons.appendChild(photoDeleteBtn);
    photoButtonsContainer.appendChild(photoButtons);

    photoManagement.appendChild(photoContainer);
    photoManagement.appendChild(photoButtonsContainer);

    const inputContainer = document.createElement("div");
    inputContainer.className = "user-data-editing-form_input-container";

    const usernameInputContainer = document.createElement("div");
    const usernameInputLabel = document.createElement("label");
    const usernameInput = document.createElement("input");
    const usernameInputError = document.createElement("div");
    const usernameInputErrorText = document.createElement("span");
    usernameInputContainer.className = "user-data-editing-form_input";
    usernameInputLabel.for = "user-data-editing-form_username";
    usernameInputLabel.textContent = "Новый юзернейм:";
    usernameInput.id = "user-data-editing-form_username";
    usernameInput.name = "username";
    usernameInput.type = "text";
    usernameInput.value = user.username;
    usernameInputError.className = "username-error";
    usernameInputError.appendChild(usernameInputErrorText);
    usernameInputContainer.append(usernameInputLabel, usernameInput, usernameInputError);

    const emailInputContainer = document.createElement("div");
    const emailInputLabel = document.createElement("label");
    const emailInput = document.createElement("input");
    const emailInputError = document.createElement("div");
    const emailInputErrorText = document.createElement("span");
    emailInputContainer.className = "user-data-editing-form_input";
    emailInputLabel.for = "user-data-editing-form_email";
    emailInputLabel.textContent = "Новая почта:";
    emailInput.id = "user-data-editing-form_email";
    emailInput.name = "email";
    emailInput.type = "text";
    emailInput.value = user.email;
    emailInputError.className = "email-error";
    emailInputError.appendChild(emailInputErrorText);
    emailInputContainer.append(emailInputLabel, emailInput, emailInputError);

    const passwordInputContainer = document.createElement("div");
    const passwordInputLabel = document.createElement("label");
    const passwordInput = document.createElement("input");
    const passwordInputError = document.createElement("div");
    const passwordInputErrorText = document.createElement("span");
    passwordInputContainer.className = "user-data-editing-form_input";
    passwordInputLabel.for = "user-data-editing-form_password";
    passwordInputLabel.textContent = "Новый пароль:";
    passwordInput.id = "user-data-editing-form_password";
    passwordInput.name = "password";
    passwordInput.type = "text";
    passwordInputError.className = "password-error";
    passwordInputError.appendChild(passwordInputErrorText);
    passwordInputContainer.append(passwordInputLabel, passwordInput, passwordInputError);

    inputContainer.appendChild(usernameInputContainer);
    inputContainer.appendChild(emailInputContainer);
    inputContainer.appendChild(passwordInputContainer);

    const submitBtnContainer = document.createElement("div");
    const submitBtn = document.createElement("button");
    submitBtnContainer.className = "user-data-editing-form_submit-button";
    submitBtn.type = "submit";
    submitBtn.textContent = "Отправить";
    submitBtnContainer.appendChild(submitBtn);

    const formError = document.createElement("div");
    const formErrorText = document.createElement("span");
    formError.className = "user-data-editing-form_error";
    formError.appendChild(formErrorText);

    form.appendChild(photoManagement);
    form.appendChild(inputContainer);
    form.appendChild(submitBtnContainer);
    form.appendChild(formError);

    container.appendChild(title);
    container.appendChild(form);

    returnBtnImg.addEventListener("click", () => {
        appendUserPage(user);
    });

    photoUploadBtn.addEventListener("click", () => {
        fileInput.click();
    });

    photoDeleteBtn.addEventListener("click", deleteFile);

    fileInput.addEventListener("change", (event) => {
        uploadFile(event);
    })

    usernameInput.addEventListener("input", (event) => {
       checkUsername(6, 16, event.target.value.trim(), usernameInputErrorText);
    });

    emailInput.addEventListener("input", (event) => {
        checkEmail(event.target.value.trim(), emailInputErrorText);
    });

    passwordInput.addEventListener("input", (event) => {
        checkPassword(8, 18, event.target.value.trim(), passwordInputErrorText);
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!checkUsername(6, 16, usernameInput.value.trim(), usernameInputErrorText)) return;
        if (!checkEmail(emailInput.value.trim(), emailInputErrorText)) return;
        if (!checkPassword(8, 18, passwordInput.value.trim(), passwordInputErrorText)) return;

        updateUser(
            !!(!emailInput.value && user.email),
            !!(photo.getAttribute("data-photo-type") === "default" && user.has_photo),
            usernameInput.value.trim() !== user.username ? usernameInput.value.trim() : null,
            passwordInput.value.trim(),
            emailInput.value.trim() !== user.email ? emailInput.value.trim() : null,
            fileInput.files[0]
        );
    });

    return container;
}

function checkUsername(ge, le, username, errorText) {
    const globalErrorText = document.querySelector(".user-data-editing-form_error span");
    globalErrorText.textContent = null;

    if (username.length < ge) {
        errorText.textContent = `Минимальная длина: ${ge} символов`;
    }
    else if (username.length > le) {
        errorText.textContent = `Максимальная длина: ${le} символов`;
    }
    else {
        errorText.textContent = null;
        return true;
    }
}

function checkEmail(email, errorText) {
    const globalErrorText = document.querySelector(".user-data-editing-form_error span");
    globalErrorText.textContent = null;

    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if ((!regex.test(email) || email.length > 40) && email.length !== 0) {
        errorText.textContent = "Невалидный адрес";
    }
    else {
        errorText.textContent = null;
        return true;
    }
}

function checkPassword(ge, le, password, errorText) {
    const globalErrorText =  document.querySelector(".user-data-editing-form_error span");
    globalErrorText.textContent = null;

    if (password.length < ge && password.length !== 0) {
        errorText.textContent = `Минимальная длина: ${ge} символов`;
    }
    else if (password.length > le) {
        errorText.textContent = `Максимальная длина: ${le} символов`;
    }
    else {
        errorText.textContent = null;
        return true;
    }
}

function uploadFile(event) {
    const photo = document.querySelector(".user-data-editing-form_photo-container img");
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = (event) => {
            photo.src = event.target.result;
            photo.setAttribute("data-photo-type", "uploaded");
        };
        reader.readAsDataURL(file);
    }
}

function deleteFile() {
    const photo = document.querySelector(".user-data-editing-form_photo-container img");
    photo.src = "/static/img/default-avatar.png";
    photo.setAttribute("data-photo-type", "default");

    const input = document.getElementById("input-user-photo");
    input.value = null;
}
