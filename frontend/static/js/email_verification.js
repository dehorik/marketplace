const form = document.querySelector("#confirmation-menu form");
const cancel_button = document.getElementById("cancel-email-button");
const title = document.querySelector(".title-form");


function confirm_email(event) {
    event.preventDefault();

    form.removeEventListener("submit", confirm_email);
    cancel_button.removeEventListener("click", exit);

    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    axios.patch("/users/email-verification", {token: token})
        .then(function (response) {
            title.style.fontWeight = "600";
            title.innerHTML = "Почта подтверждена!"
            setTimeout(exit, 3000);
        })
        .catch(function (error) {
            if (error.response.status === 400) {
                title.style.fontWeight = "600";
                title.innerHTML = "Время истекло!";
            }

            setTimeout(exit, 3000);
        });
}

function exit() {
    window.location.href = "/";
}


form.addEventListener("submit", confirm_email);
cancel_button.addEventListener("click", exit);
