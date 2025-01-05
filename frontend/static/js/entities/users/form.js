function appendUserForm(user) {
    const container = document.querySelector(".user-page_container");

    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    container.appendChild(getUserForm(user));
}

function getUserForm(user) {
    const container = document.createElement("div");
    container.className = "user-data-editing-form";

    const title = document.createElement("div");
    title.className = "user-data-editing-form_title";

    const title_return_btn = document.createElement("div");
    const return_btn_img = document.createElement("img");
    title_return_btn.className = "user-data-editing-form_title-return-btn";
    return_btn_img.src = "/static/img/back.png";
    return_btn_img.alt = "back";
    title_return_btn.appendChild(return_btn_img);
    const title_text_container = document.createElement("div");
    const title_text = document.createElement("span");
    title_text_container.className = "user-data-editing-form_title-text";
    title_text.textContent = "Изменение данных пользователя";
    title_text_container.appendChild(title_text);

    title.appendChild(title_return_btn);
    title.appendChild(title_text_container);

    const form = document.createElement("form");
    form.autocomplete = "off";

    const photo_management = document.createElement("div");
    photo_management.className = "user-data-editing-form_photo-management";

    const photo_container = document.createElement("div");
    photo_container.className = "user-data-editing-form_photo-container";
    const photo = document.createElement("img");
    photo.alt = "user";

    if (user.photo_path) {
        photo.src = `/${user.photo_path}?reload=${Date.now()}`;
        photo.setAttribute("data-photo-type", "uploaded");
    }
    else {
        photo.src = "/static/img/default-avatar.png";
        photo.setAttribute("data-photo-type", "default");
    }

    photo_container.appendChild(photo);

    const photo_buttons_container = document.createElement("div");
    photo_buttons_container.className = "user-data-editing-form_photo-buttons-container";
    const photo_buttons = document.createElement("div");
    photo_buttons.className = "user-data-editing-form_photo-buttons";

    const photo_upload_btn = document.createElement("div");
    const photo_upload_btn_text = document.createElement("span");
    const photo_input_elem = document.createElement("input");
    photo_upload_btn_text.textContent = "Загрузить фото";
    photo_input_elem.id = "input-user-photo";
    photo_input_elem.name = "photo";
    photo_input_elem.className = "no-display";
    photo_input_elem.type = "file";
    photo_input_elem.accept = ".jpg, .png";
    photo_upload_btn.appendChild(photo_upload_btn_text);
    photo_upload_btn.appendChild(photo_input_elem);

    const photo_delete_btn = document.createElement("div");
    const photo_delete_btn_text = document.createElement("span");
    photo_delete_btn_text.textContent = "Удалить фото";
    photo_delete_btn.appendChild(photo_delete_btn_text);

    photo_buttons.appendChild(photo_upload_btn);
    photo_buttons.appendChild(photo_delete_btn);
    photo_buttons_container.appendChild(photo_buttons);

    photo_management.appendChild(photo_container);
    photo_management.appendChild(photo_buttons_container);

    const input_container = document.createElement("div");
    input_container.className = "user-data-editing-form_input-container";

    const username_input_container = document.createElement("div");
    const username_input_label = document.createElement("label");
    const username_input = document.createElement("input");
    const username_input_error = document.createElement("div");
    const username_input_error_text = document.createElement("span");
    username_input_container.className = "user-data-editing-form_input";
    username_input_label.for = "user-data-editing-form_username";
    username_input_label.textContent = "Новый юзернейм:";
    username_input.id = "user-data-editing-form_username";
    username_input.name = "username";
    username_input.type = "text";
    username_input.value = user.username;
    username_input_error.className = "username-error";
    username_input_error.appendChild(username_input_error_text);
    username_input_container.append(username_input_label, username_input, username_input_error);

    const email_input_container = document.createElement("div");
    const email_input_label = document.createElement("label");
    const email_input = document.createElement("input");
    const email_input_error = document.createElement("div");
    const email_input_error_text = document.createElement("span");
    email_input_container.className = "user-data-editing-form_input";
    email_input_label.for = "user-data-editing-form_email";
    email_input_label.textContent = "Новая почта:";
    email_input.id = "user-data-editing-form_email";
    email_input.name = "email";
    email_input.type = "text";
    email_input.value = user.email;
    email_input_error.className = "email-error";
    email_input_error.appendChild(email_input_error_text);
    email_input_container.append(email_input_label, email_input, email_input_error);

    const password_input_container = document.createElement("div");
    const password_input_label = document.createElement("label");
    const password_input = document.createElement("input");
    const password_input_error = document.createElement("div");
    const password_input_error_text = document.createElement("span");
    password_input_container.className = "user-data-editing-form_input";
    password_input_label.for = "user-data-editing-form_password";
    password_input_label.textContent = "Новый пароль:";
    password_input.id = "user-data-editing-form_password";
    password_input.name = "password";
    password_input.type = "text";
    password_input_error.className = "password-error";
    password_input_error.appendChild(password_input_error_text);
    password_input_container.append(password_input_label, password_input, password_input_error);

    input_container.appendChild(username_input_container);
    input_container.appendChild(email_input_container);
    input_container.appendChild(password_input_container);

    const submit_btn_container = document.createElement("div");
    const submit_btn = document.createElement("button");
    submit_btn_container.className = "user-data-editing-form_submit-button";
    submit_btn.type = "submit";
    submit_btn.textContent = "Отправить";
    submit_btn_container.appendChild(submit_btn);

    const form_error = document.createElement("div");
    const form_error_text = document.createElement("span");
    form_error.className = "user-data-editing-form_error";
    form_error.appendChild(form_error_text);

    form.appendChild(photo_management);
    form.appendChild(input_container);
    form.appendChild(submit_btn_container);
    form.appendChild(form_error);

    container.appendChild(title);
    container.appendChild(form);

    return_btn_img.addEventListener("click", () => {
        appendUserPage(user);
    });

    photo_upload_btn.addEventListener("click", () => {
        photo_input_elem.click();
    });

    photo_delete_btn.addEventListener("click", deleteFile);

    photo_input_elem.addEventListener("change", (event) => {
        uploadFile(event);
    })

    username_input.addEventListener("input", (event) => {
       checkUsername(6, 16, event.target, username_input_error_text);
    });

    email_input.addEventListener("input", (event) => {
        checkEmail(event.target, email_input_error_text);
    });

    password_input.addEventListener("input", (event) => {
        checkPassword(8, 18, event.target, password_input_error_text);
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!checkUsername(6, 16, username_input, username_input_error_text)) return;
        if (!checkEmail(email_input, email_input_error_text)) return;
        if (!checkPassword(8, 18, password_input, password_input_error_text)) return;

        updateUser(event.target, user);
    });

    return container;
}

function checkUsername(ge, le, node, error_node) {
    const global_error = document.querySelector(".user-data-editing-form_error span");
    global_error.textContent = null;

    if (node.value.length < ge) {
        error_node.textContent = `Минимальная длина: ${ge} символов`;
    }
    else if (node.value.length > le) {
        error_node.textContent = `Максимальная длина: ${le} символов`;
    }
    else {
        error_node.textContent = null;
        return true;
    }
}

function checkEmail(node, error_node) {
    const global_error = document.querySelector(".user-data-editing-form_error span");
    global_error.textContent = null;

    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if ((!regex.test(node.value) || node.value.length > 40) && node.value.length !== 0) {
        error_node.textContent = "Невалидный адрес";
    }
    else {
        error_node.textContent = null;
        return true;
    }
}

function checkPassword(ge, le, node, error_node) {
    const global_error = document.querySelector(".user-data-editing-form_error span");
    global_error.textContent = null;

    if (node.value.length < ge && node.value.length !== 0) {
        error_node.textContent = `Минимальная длина: ${ge} символов`;
    }
    else if (node.value.length > le) {
        error_node.textContent = `Максимальная длина: ${le} символов`;
    }
    else {
        error_node.textContent = null;
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
