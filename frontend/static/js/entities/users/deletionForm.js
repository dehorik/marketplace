function appendUserDeletionForm(user) {
    const container = document.querySelector(".user-page_container");

    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    container.appendChild(getUserDeletionForm(user));
}

function getUserDeletionForm(user) {
    const container = document.createElement("div");
    container.className = "user-deletion-form";

    const title = document.createElement("div");
    const title_text = document.createElement("span");
    title.className = "user-deletion-form_title";
    title_text.textContent = "Удалить ваш аккаунт?";
    title.appendChild(title_text);

    const buttons_container = document.createElement("div");
    buttons_container.className = "user-deletion-form_buttons";

    const return_button = document.createElement("div");
    const return_button_text = document.createElement("span");
    return_button_text.textContent = "Нет, я хочу остаться";
    return_button.appendChild(return_button_text);

    const delete_button = document.createElement("div");
    const delete_button_text = document.createElement("span");
    delete_button_text.textContent = "Да, удалить мой аккаунт";
    delete_button.appendChild(delete_button_text);

    buttons_container.appendChild(return_button);
    buttons_container.appendChild(delete_button);

    const error = document.createElement("div");
    const error_text = document.createElement("span");
    error.className = "user-deletion-form_error";
    error.appendChild(error_text);

    container.appendChild(title);
    container.appendChild(buttons_container);
    container.appendChild(error);

    return_button.addEventListener("click", () => {
        appendUserPage(user);
    })

    delete_button.addEventListener("click", deleteUser);

    return container;
}
