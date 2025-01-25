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
    const titleText = document.createElement("span");
    title.className = "user-deletion-form_title";
    titleText.textContent = "Удалить ваш аккаунт?";
    title.appendChild(titleText);

    const buttonsContainer = document.createElement("div");
    buttonsContainer.className = "user-deletion-form_buttons";

    const returnButton = document.createElement("div");
    const returnButtonText = document.createElement("span");
    returnButtonText.textContent = "Нет, я хочу остаться";
    returnButton.appendChild(returnButtonText);

    const deleteButton = document.createElement("div");
    const deleteButtonText = document.createElement("span");
    deleteButtonText.textContent = "Да, удалить мой аккаунт";
    deleteButton.appendChild(deleteButtonText);

    buttonsContainer.appendChild(returnButton);
    buttonsContainer.appendChild(deleteButton);

    const error = document.createElement("div");
    const errorText = document.createElement("span");
    error.className = "user-deletion-form_error";
    error.appendChild(errorText);

    container.appendChild(title);
    container.appendChild(buttonsContainer);
    container.appendChild(error);

    returnButton.addEventListener("click", () => {
        appendUserPage(user);
    })

    deleteButton.addEventListener("click", deleteUser);

    return container;
}
