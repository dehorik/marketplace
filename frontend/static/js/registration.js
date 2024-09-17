const input_username_elem = document.getElementById("input-username");
const input_password_elem = document.getElementById("input-password");
const password_viewer = document.getElementById("password-view-checkbox");
const form = document.querySelector("#registration-form-container form")


input_username_elem.addEventListener("input", function () {
    const invalid_elem_msg = document.querySelector("#username-input-container .invalid-input-msg");

    if (input_username_elem.validity.tooShort) {
        invalid_elem_msg.innerHTML = "Минимальная длина: 6 символов";
    }
    else {
        invalid_elem_msg.innerHTML = "";
    }
});

input_password_elem.addEventListener("input", function () {
    const invalid_elem_msg = document.querySelector("#password-input-container .invalid-input-msg");

    if (input_password_elem.validity.tooShort) {
        invalid_elem_msg.innerHTML = "Минимальная длина: 8 символов";
    }
    else {
        invalid_elem_msg.innerHTML = "";
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

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const form_data = new FormData(form);

    axios.post("/auth/registration", form_data)
        .then(function (response) {
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
        })
        .catch(function (error) {
            if (error.response.status === 400) {
                const invalid_elem_msg = document.querySelector("#username-input-container .invalid-input-msg");
                invalid_elem_msg.innerHTML = "Имя пользователя уже занято!";
            }
        });
});
