const input_username_elem = document.getElementById("input-username");
const input_password_elem = document.getElementById("input-password");
const password_view_checkbox = document.getElementById("password-view-checkbox");
const invalid_username_msg = document.querySelector("#username-input-container .invalid-input-msg");
const invalid_password_msg = document.querySelector("#password-input-container .invalid-input-msg");


input_username_elem.addEventListener("input", function () {
    if (input_username_elem.value.length < 6) {
        invalid_username_msg.innerHTML = "Минимальная длина: 6 символов";
    }
    else if (input_username_elem.value.length > 16) {
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

input_password_elem.addEventListener("input", function () {
    if (input_password_elem.value.length < 8) {
        invalid_password_msg.innerHTML = "Минимальная длина: 8 символов";
    }
    else if (input_password_elem.value.length > 18) {
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

input_username_elem.addEventListener("blur", () => {
    if (input_username_elem.value.length === 0) {
        invalid_username_msg.innerHTML = "";
    }
});

input_password_elem.addEventListener("blur", () => {
    if (input_password_elem.value.length === 0) {
        invalid_password_msg.innerHTML = "";
    }
});

password_view_checkbox.addEventListener("click", function () {
    if (password_view_checkbox.checked) {
        input_password_elem.type = "password";
    }
    else {
        input_password_elem.type = "text";
    }
});


function validate_form_data() {
    if (input_username_elem.value.length > 16) {
        return false;
    }
    else if (input_username_elem.value.length < 6) {
        return false;
    }

    if (input_password_elem.value.length > 18) {
        return false;
    }
    else if (input_password_elem.value.length < 8) {
        return false;
    }

    return true;
}
