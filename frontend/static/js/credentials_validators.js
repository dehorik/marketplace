const username_field = document.getElementById("username-field");
const password_field = document.getElementById("password-field");
const password_view_checkbox = document.getElementById("password-checkbox");
const invalid_username_msg = document.querySelector("#username-node .invalid-input");
const invalid_password_msg = document.querySelector("#password-node .invalid-input");


username_field.addEventListener("input", function () {
    if (username_field.value.length < 6) {
        invalid_username_msg.innerHTML = "Минимальная длина: 6 символов";
    }
    else if (username_field.value.length > 16) {
        invalid_username_msg.innerHTML = "Максимальная длина: 16 символов";
    }
    else if (6 <= invalid_username_msg.length <= 16 && 8 <= invalid_password_msg.length <= 18) {
        invalid_username_msg.innerHTML = "";
        invalid_password_msg.innerHTML = "";
    }
    else {
        invalid_username_msg.innerHTML = "";
    }
});

password_field.addEventListener("input", function () {
    if (password_field.value.length < 8) {
        invalid_password_msg.innerHTML = "Минимальная длина: 8 символов";
    }
    else if (password_field.value.length > 18) {
        invalid_password_msg.innerHTML = "Максимальная длина: 18 символов";
    }
    else if (6 <= invalid_username_msg.length <= 16 && 8 <= invalid_password_msg.length <= 18) {
        invalid_username_msg.innerHTML = "";
        invalid_password_msg.innerHTML = "";
    }
    else {
        invalid_password_msg.innerHTML = "";
    }
});


username_field.addEventListener("blur", () => {
    if (username_field.value.length === 0) {
        invalid_username_msg.innerHTML = "";
    }
});

password_field.addEventListener("blur", () => {
    if (password_field.value.length === 0) {
        invalid_password_msg.innerHTML = "";
    }
});


password_view_checkbox.addEventListener("click", function () {
    if (password_view_checkbox.checked) {
        password_field.type = "password";
    }
    else {
        password_field.type = "text";
    }
});


function validate_form_data() {
    if (username_field.value.length > 16) {
        return false;
    }
    else if (username_field.value.length < 6) {
        return false;
    }
    else if (password_field.value.length > 18) {
        return false;
    }
    else if (password_field.value.length < 8) {
        return false;
    }

    return true;
}
