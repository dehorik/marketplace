window.addEventListener("load", initAuthForm);


function initAuthForm() {
    const container = document.querySelector(".auth-form_container");
    const form = container.querySelector("form");
    const formTypeChanger = container.querySelector(".auth-form_form-type-changer_button");
    const usernameInput = document.getElementById("auth-form_username");
    const passwordInput = document.getElementById("auth-form_password");
    const usernameErrorText = document.querySelector(".auth-form_username-error span");
    const passwordErrorText = document.querySelector(".auth-form_password-error span");

    formTypeChanger.addEventListener("click", () => {
        changeFormType(container);
    });

    usernameInput.addEventListener("input", (event) => {
        checkCredentials(6, 16, event.target.value.trim(), usernameErrorText);
    });

    passwordInput.addEventListener("input", (event) => {
        checkCredentials(8, 18, event.target.value.trim(), passwordErrorText);
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!checkCredentials(6, 16, usernameInput.value.trim(), usernameErrorText)) return;
        if (!checkCredentials(8, 18, passwordInput.value.trim(), passwordErrorText)) return;

        if (container.getAttribute("data-form-type") === "login") {
            login(usernameInput.value.trim(), passwordInput.value.trim());
        }
        else if (container.getAttribute("data-form-type") === "reg") {
            registration(usernameInput.value.trim(), passwordInput.value.trim());
        }
    });
}

function changeFormType(container) {
    const title = container.querySelector(".auth-form_title span");
    const submitBtn = container.querySelector(".auth-form_submit-button button");
    const formTypeChangerText = container.querySelector(".auth-form_form-type-changer_title span");
    const formTypeChangerBtn = container.querySelector(".auth-form_form-type-changer_button span");
    const usernameInput = document.getElementById("auth-form_username");
    const passwordInput = document.getElementById("auth-form_password");
    const usernameErrorText = document.querySelector(".auth-form_username-error span");
    const passwordErrorText = document.querySelector(".auth-form_password-error span");
    const errorText = document.querySelector(".auth-form_error-message span");

    if (container.getAttribute("data-form-type") === "login") {
        container.setAttribute("data-form-type", "reg");

        title.textContent = "Регистрация";
        submitBtn.textContent = "Создать аккаунт";
        formTypeChangerText.textContent = "Уже есть аккаунт?";
        formTypeChangerBtn.textContent = "Вход в аккаунт";
    }
    else if (container.getAttribute("data-form-type") === "reg") {
        container.setAttribute("data-form-type", "login");

        title.textContent = "Вход в аккаунт";
        submitBtn.textContent = "Войти в аккаунт";
        formTypeChangerText.textContent = "Ещё нет аккаунта?";
        formTypeChangerBtn.textContent = "Регистрация";
    }

    usernameInput.value = null;
    passwordInput.value = null;
    usernameErrorText.textContent = null;
    passwordErrorText.textContent = null;
    errorText.textContent = null;
}

function checkCredentials(ge, le, value, errorText) {
    document.querySelector(".auth-form_error-message span").textContent = null;

    if (value.length < ge) {
        errorText.textContent = `Минимальная длина: ${ge} символов`;
    }
    else if (value.length > le) {
        errorText.textContent = `Максимальная длина: ${le} символов`;
    }
    else {
        errorText.textContent = null;
        return true;
    }
}
