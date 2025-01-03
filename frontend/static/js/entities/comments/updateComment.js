function updateComment(form, old_comment) {
    const comment_id = old_comment.comment_id;
    const rating = document.querySelector(".comment-form-rating-stars-container").getAttribute("data-rating");
    const text = form.querySelector("#comment-form-text").value;
    const file = form.querySelector(".comment-form-upload-button input").files[0];
    const photo_type = form.querySelector(".comment-form-photo img").getAttribute("data-photo-type");

    const data = new FormData();

    if (!text && old_comment.text) {
        data.append("clear_text", "true");
    }
    else {
        data.append("clear_text", "false");
    }

    if (photo_type === "default" && old_comment.comment_photo_path) {
        data.append("clear_photo", "true");
    }
    else {
        data.append("clear_photo", "false");
    }

    if (Number(rating) !== old_comment.rating) {
        data.append("rating", rating);
    }

    if (text && text !== old_comment.text) {
        data.append("text", text);
    }

    if (file) {
        data.append("photo", file);
    }

    getVerifiedToken().then((token) => {
        axios({
            url: `/comments/${comment_id}`,
            method: "patch",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
            data: data
        })
            .then((response) => {
                for (let node of document.querySelectorAll(".comments-grid .comment")) {
                    if (Number(node.getAttribute("data-comment-id")) === response.data.comment_id) {
                        let old_comment_data_container = node.querySelector(".comment-data-container");
                        let old_comment_head = node.querySelector(".comment-head");
                        let old_comment_rating_bar = old_comment_head.querySelectorAll(".comment-stars img");
                        let old_comment_text = old_comment_data_container.querySelector(".comment-text");
                        let old_comment_photo = old_comment_data_container.querySelector(".comment-photo img");

                        for (let i = 1; i < 6; i++) {
                            if (response.data.rating >= i) {
                                old_comment_rating_bar[i-1].src = "/static/img/active_star.png";
                            }
                            else {
                                old_comment_rating_bar[i-1].src = "/static/img/inactive_star.png";
                            }
                        }

                        old_comment_rating_bar[0].parentNode.setAttribute("data-rating", response.data.rating);

                        if (response.data.text && old_comment_text) {
                            old_comment_text.textContent = response.data.text;
                        }

                        else if (response.data.text && !old_comment_text) {
                            let comment_text = document.createElement("div");
                            comment_text.className = "comment-text";
                            comment_text.textContent = response.data.text;

                            old_comment_head.after(comment_text);
                        }

                        else if (!response.data.text && old_comment_text) {
                            old_comment_data_container.removeChild(old_comment_text);
                        }

                        if (response.data.photo_path && old_comment_photo) {
                            old_comment_photo.src = `/${response.data.photo_path}?reload=${Date.now()}`;
                        }

                        else if (response.data.photo_path && !old_comment_photo) {
                            let comment_photo_container = document.createElement("div");
                            let comment_photo = document.createElement("img");
                            comment_photo_container.className = "comment-photo";
                            comment_photo.src = `/${response.data.photo_path}`;
                            comment_photo.alt = "photo";
                            comment_photo_container.append(comment_photo);

                            if (old_comment_text) {
                                old_comment_text.after(comment_photo_container);
                            }
                            else if (response.data.text) {
                                old_comment_data_container.append(comment_photo_container);
                            }
                            else {
                                old_comment_head.after(comment_photo_container);
                            }
                        }

                        else if (!response.data.photo_path && old_comment_photo) {
                            old_comment_data_container.removeChild(old_comment_photo.parentNode);
                        }
                    }
                }

                recalculateProductRating();
                removeForm();
            })
            .catch((error) => {
                const error_text = document.querySelector(".comment-form-error-message span");

                if (error.status === 422 || error.status === 400) {
                    error_text.textContent = "Ошибка в введённых данных";
                }

                else if (error.status === 415) {
                    error_text.textContent = "Невалидный файл";
                }

                else if (error.status === 404) {
                    error_text.textContent = "Отзыв не существует";
                }

                else if (error.status === 401 || error.status === 403) {
                    error_text.textContent = "Ошибка аутентификации";
                }

                else {
                    error_text.textContent = "Ошибка редактирования отзыва";
                }
            });
    });
}
