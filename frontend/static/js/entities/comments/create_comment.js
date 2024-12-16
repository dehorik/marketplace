window.addEventListener("load", () => {
    const comment_creation_button = document.querySelector(".comment-creation-link");
    comment_creation_button.addEventListener("click", () => {
        for (let node of document.body.children) {
            node.classList.add("no-display");
        }

        const form = get_form();
        document.body.prepend(form);
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
            const comments_message = grid.querySelector(".comments-message");

            if (comments_message) {
                grid.removeChild(comments_message);
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
                    grid.prepend(create_node(response.data.comments[0]));
                    recalculate_product_rating();
                    return_product();
                });
        })
        .catch((error) => {
            const message_area = document.querySelector(".comment-form-error-message span");

            if (error.status === 422) {
                message_area.textContent = "Ошибка в введённых данных!";
            }

            else if (error.status === 415) {
                message_area.textContent = "Невалидный файл!";
            }

            else if (error.status === 404) {
                message_area.textContent = "Отзыв не создан: товар или пользователь не существуют";
            }

            else if (error.status === 401 || error.status === 403) {
                message_area.textContent = "Отзыв не создан: ошибка аутентификации";
            }

            else {
                message_area.textContent = "Отзыв не был создан: возникли проблемы во время операции";
            }
        });
}
