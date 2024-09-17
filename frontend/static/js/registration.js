const form = document.querySelector("#registration-form-container form");


form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (input_username_elem.value.length > 16 && !(input_username_elem.name === "user_email")) {
        return;
    }
    else if (input_username_elem.value.length < 6) {
        return;
    }

    if (input_password_elem.value.length > 18) {
        return;
    }
    else if (input_password_elem.value.length < 8) {
        return;
    }

    const form_data = new FormData(form);

    axios.post("/auth/registration", form_data)
        .then(function (response) {
            successful_auth(response);
        })
        .catch(function (error) {
            if (error.response.status === 400) {
                const invalid_elem_msg = document.querySelector("#username-input-container .invalid-input-msg");
                invalid_elem_msg.innerHTML = "Имя пользователя уже занято!";
            }
        });
});
