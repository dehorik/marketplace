const container = document.querySelector(".auth-form_container");
const form = document.querySelector(".auth-form_container form");
const username = document.getElementById("auth-form_username");
const password = document.getElementById("auth-form_password");
const username_error = document.querySelector(".auth-form_username-error span");
const password_error = document.querySelector(".auth-form_password-error span");
const footer = document.querySelector(".auth-form_footer span");


window.addEventListener("load", () => {
    const form_type_changer = container.querySelector(".auth-form_form-type-changer_button");

    form_type_changer.addEventListener("click", changeFormType);

    username.addEventListener("input", () => {
        checkCredentials(6, 16, username.value, username_error);
    })

    password.addEventListener("input", () => {
        checkCredentials(8, 18, password.value, password_error);
    })

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!checkCredentials(6, 16, username.value, username_error)) return;
        if (!checkCredentials(8, 18, password.value, password_error)) return;

        if (container.getAttribute("data-form-type") === "login") {
            login(username.value, password.value);
        }
        else if (container.getAttribute("data-form-type") === "reg") {
            registration(username.value, password.value);
        }
    })
});


function changeFormType() {
    const form_title = container.querySelector(".auth-form_title span");
    const form_submit_button = container.querySelector(".auth-form_submit-button button");
    const form_type_changer_title = container.querySelector(".auth-form_form-type-changer_title span");
    const form_type_changer_button = container.querySelector(".auth-form_form-type-changer_button span");

    if (container.getAttribute("data-form-type") === "login") {
        container.setAttribute("data-form-type", "reg");

        form_title.textContent = "Регистрация";
        form_submit_button.textContent = "Создать аккаунт";
        form_type_changer_title.textContent = "Уже есть аккаунт?";
        form_type_changer_button.textContent = "Вход в аккаунт";
    }
    else if (container.getAttribute("data-form-type") === "reg") {
        container.setAttribute("data-form-type", "login");

        form_title.textContent = "Вход в аккаунт";
        form_submit_button.textContent = "Войти в аккаунт";
        form_type_changer_title.textContent = "Ещё нет аккаунта?";
        form_type_changer_button.textContent = "Регистрация";
    }

    username.value = null;
    password.value = null;

    username_error.textContent = null;
    password_error.textContent = null;

    footer.textContent = "Webstore";
}

function checkCredentials(ge, le, value, error_node) {
    footer.textContent = "Webstore";

    if (value.length === 0) {
        error_node.textContent = null;
    }
    else if (value.length < ge) {
        error_node.textContent = `Минимальная длина: ${ge} символов`;
    }
    else if (value.length > le) {
        error_node.textContent = `Максимальная длина: ${le} символов`;
    }
    else {
        error_node.textContent = null;
        return true;
    }
}
