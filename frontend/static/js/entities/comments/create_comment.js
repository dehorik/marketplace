function createComment(form) {
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

            let created_comment_data = response.data;

            axios({
                url: "/users/me",
                method: "get",
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                }
            })
                .then((response) => {
                    let user_data = response.data;

                    let comment = {
                        comment_id: created_comment_data.comment_id,
                        user_id: user_data.user_id,
                        product_id: created_comment_data.product_id,
                        username: user_data.username,
                        user_photo_path: user_data.photo_path,
                        rating: created_comment_data.rating,
                        creation_date: created_comment_data.creation_date,
                        text: created_comment_data.text,
                        comment_photo_path: created_comment_data.photo_path
                    }

                    grid.prepend(createNode(comment));
                    recalculateProductRating();
                    removeForm();
                });
        })
        .catch((error) => {
            const error_text = document.querySelector(".comment-form-error-message span");

            if (error.status === 422) {
                error_text.textContent = "Ошибка в введённых данных";
            }

            else if (error.status === 415) {
                error_text.textContent = "Невалидный файл";
            }

            else if (error.status === 404) {
                error_text.textContent = "Товар или пользователь не существуют";
            }

            else if (error.status === 401 || error.status === 403) {
                error_text.textContent = "Ошибка аутентификации";
            }

            else {
                error_text.textContent = "Ошибка создания отзыва";
            }
        });
}
