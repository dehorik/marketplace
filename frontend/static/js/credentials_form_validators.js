const input_username_elem = document.getElementById("input-username");
const input_password_elem = document.getElementById("input-password");
const password_viewer = document.getElementById("password-view-checkbox");
const invalid_username_msg = document.querySelector("#username-input-container .invalid-input-msg");
const invalid_password_msg = document.querySelector("#password-input-container .invalid-input-msg");


input_username_elem.addEventListener("input", function () {
    if (input_username_elem.value.length < 6) {
        invalid_username_msg.innerHTML = "Минимальная длина: 6 символов";
    }
    else if (input_username_elem.name === "user_email" && input_username_elem.value.length > 32) {
        invalid_username_msg.innerHTML = "Максимальная длина: 32 символа";
    }
    else if (input_username_elem.name === "user_name" && input_username_elem.value.length > 16) {
        invalid_username_msg.innerHTML = "Максимальная длина: 16 символов";
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

password_viewer.addEventListener("click", function () {
    if (password_viewer.checked) {
        input_password_elem.type = "password";
    }
    else {
        input_password_elem.type = "text";
    }
});


function successful_auth(response) {
    const access_token = response.data.token.access_token;
    const user = response.data.user;
    set_token(access_token);

    const new_body = document.createElement("body");
    const message_elem = document.createElement('div');
    message_elem.id = "successful_auth_message";
    message_elem.innerHTML = `Добро пожаловать, ${user.user_name}!`;
    new_body.append(message_elem);
    document.body.replaceWith(new_body);

    const text = message_elem.textContent;
    message_elem.innerHTML = text.replace(/./g, '<span class="new">$&</span>');

    const span_elems= message_elem.querySelectorAll('span.new');
    span_elems.forEach((span, i) => {
        setTimeout(() => {
            span.classList.add('div_opacity');
        }, 40 * i);
    });

    setTimeout( () => {
            window.location.href = '/products/list';
        },
        1410
    );
}
