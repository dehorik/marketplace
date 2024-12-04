window.addEventListener("load", () => {
    const comment_creation_button = document.querySelector(".comment-creation-link");
    comment_creation_button.addEventListener("click", () => {
        for (let node of document.body.children) {
            node.classList.add("no-display");
        }

        const form = get_form();
        document.body.appendChild(form);
    });
});


function create_comment(form) {
    const product_id = window.location.pathname.split("/").slice(-1)[0];

    const rating = document.querySelector(".comment-form-rating-stars-container").getAttribute("data-rating");
    const text = form.querySelector("#comment-form-text").value;
    const file = form.querySelector(".comment-form-upload-button input").files[0];

    const data = new FormData();

    data.append("product_id", product_id);
    data.append("rating", rating);

    if (text) {
        data.append("text", text);
    }

    if (file) {
        data.append("photo", file);
    }

    axios({
        url: "/comments",
        method: "post",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        data: data
    })
        .then((response) => {
            append_response("Отзыв успешно создан!");

            setTimeout(() => {
                const message_area = grid.querySelector(".comments-message");

                if (message_area) {
                    grid.removeChild(message_area);
                }

                // временное решение!!!
                axios({
                    url: "/comments/latest",
                    method: "get",
                    params: {
                        product_id: response.data.product_id,
                        amount: 1,
                        last_id: response.data.comment_id + 1
                    }
                })
                    .then((response) => {
                        append_comment(response.data.comments[0]);
                        redirect_to_product();
                    });
            }, 2700);
        })
        .catch((error) => {
            if (error.status === 422) {
                const message_area = document.querySelector(".comment-form-error-message span");
                message_area.textContent = "Ошибка в введённых данных!";
            }

            else if (error.status === 415) {
                const message_area = document.querySelector(".comment-form-error-message span");
                message_area.textContent = "Невалидный файл!";
            }

            else if (error.status === 404) {
                append_response("Отзыв не создан: товар или пользователь не существует");
                setTimeout(redirect_to_product, 2700);
            }

            else if (error.status === 401 || error.status === 403) {
                append_response("Отзыв не создан: ошибка аутентификации");
                setTimeout(redirect_to_product, 2700);
            }

            else {
                append_response("Отзыв не создан: возникли проблемы во время операции");
                setTimeout(redirect_to_product, 2700);
            }
        });
}
