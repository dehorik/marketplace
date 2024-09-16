const input_username_elem = document.getElementById("input-username");
const input_password_elem = document.getElementById("input-password");

input_username_elem.addEventListener("input", function () {
    const invalid_elem_msg = document.querySelector("#username-input-container .invalid-input-msg");

    if (input_username_elem.validity.tooShort) {
        invalid_elem_msg.innerHTML = "Минимальная длина: 6 символов!";
    }
    else {
        invalid_elem_msg.innerHTML = "";
    }
});

input_password_elem.addEventListener("input", function () {
    const invalid_elem_msg = document.querySelector("#password-input-container .invalid-input-msg");

    if (input_password_elem.validity.tooShort) {
        invalid_elem_msg.innerHTML = "Минимальная длина: 8 символов!";
    }
    else {
        invalid_elem_msg.innerHTML = "";
    }
});


const password_viewer = document.getElementById("password-view-checkbox");

password_viewer.addEventListener("click", function () {
    if (password_viewer.checked) {
        input_password_elem.type = "password";
    }
    else {
        input_password_elem.type = "text";
    }
});