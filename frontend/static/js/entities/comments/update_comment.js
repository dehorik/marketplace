window.addEventListener("load", () => {
    const state = new CommentEditingState();
    const comment = state.get("comment");

    const rating_bar = document.querySelectorAll(".comment-form-rating-bar a img");
    const form = document.querySelector(".comment-form-container form");
    const textarea = document.getElementById("comment-form-text");
    const comment_photo = document.querySelector(".comment-form-photo img");
    const photo_upload_button = document.querySelector(".comment-form-upload-button");
    const photo_upload_node = document.querySelector(".comment-form-upload-button input");
    const photo_delete_button = document.querySelector(".comment-form-delete-button");

    for (let i = 0; i < 5; i++) {
        rating_bar[i].addEventListener("click", (event) => {
            make_stars_active(event.target);
        });

        if (Number(comment.rating) > i) {
            rating_bar[i].src = "/static/img/active_star.png";
            rating_bar[i].setAttribute("data-state", "1");
        }
    }

    rating_bar[0].parentNode.parentNode.setAttribute("data-rating", comment.rating)

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (check_comment_text(textarea) && check_rating()) {
            update_comment(event.target);
        }
    });

    textarea.addEventListener("input", function (event) {
        check_comment_text(event.target);
    });
    textarea.value = comment.text;

    if (comment.comment_photo_path) {
        comment_photo.src = `/${comment.comment_photo_path}`;
    }
    else {
        comment_photo.src = "/static/img/empty_photo.png";
    }

    photo_upload_button.addEventListener("click", function () {
        photo_upload_node.click();
    });

    photo_upload_node.addEventListener("change", function (event) {
        upload_photo(event.target);
    });

    photo_delete_button.addEventListener("click", function () {
        delete_photo();
    });
});


function update_comment(form) {
    const state = new CommentEditingState();
    const comment = state.get("comment");

    const comment_id = comment.comment_id;
    const product_id = comment.product_id;

    const rating_bar = document.querySelector(".comment-form-rating-bar");
    const rating = rating_bar.getAttribute("data-rating");
    const text = form.querySelector("#comment-form-text").value;
    const photo = form.querySelector(".comment-form-upload-button input").files[0];

    const data = new FormData();

    if (comment.rating !== Number(rating)) {
        data.append("rating", rating)
    }

    if (comment.text !== null && !text) {
        data.append("clear_text", "true");
    }
    else if (text && comment.text !== text ) {
        data.append("text", text);
    }

    if (state.get("clear_photo")) {
        data.append("clear_photo", "true");
    }
    else if (photo) {
        data.append("photo", photo);
    }

    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJpYXQiOjE3MzMwNzE1NDYsImV4cCI6MTczMzE2MTU0Nn0.l4WW1Rh8QdZtVsHAiR_IVZalKk6H3YZlMY4N1ueIt6qZHW02wH-Whh8n4k1sZWqJQHZnUvDIsD-GgQtKxviFMLvXcCUgkFSYjLkQ02LhPxVQ68VFIvaqxLV9fJAzIqEJ4XvsNgRnfvgWLuUdHaPNLe5huXjJpI1jSfddMcZ9DwfsYQuCJi7548wbZHfGRZLRXJhmrSdAC5LqEOdQbSy1G46HGZHIx4uGc4cDTECfmU-YSzhq3bOTfyHh5izId-ZCrM_PV6Ka7Uc-6PwjYEkhhIzEEeMyZXToYoKn-5brxeqJOrJA2ZFEN1XwS7H0Nbswu6BOyb6u8MXFb5UNyLsu-Q";

    axios({
        url: `/comments/${comment_id}`,
        method: "patch",
        headers: {
            "Authorization": `Bearer ${jwt}`,
            "Content-Type": " multipart/form-data"
        },
        data: data
    })
        .then(() => {
            append_response_window(
                "Отзыв успешно изменён!",
                `/products/${product_id}`
            );
        })
        .catch((response) => {
            console.log(response)
            if (response.status === 422 || response.status === 415 || response.status === 400) {
                const message_area = document.querySelector(".comment-form-error-message span");
                message_area.textContent = "Ошибка в введённых данных!";
            }

            else if (response.status === 404) {
                append_response_window(
                    "Отзыв не существует",
                    `/products/${product_id}`
                );
            }

            else if (response.status === 401 || response.status === 403) {
                append_response_window(
                    "Отзыв не изменён: ошибка аутентификации",
                    `/products/${product_id}`
                );
            }

            else {
                append_response_window(
                    "Ошибка создания отзыва",
                    `/products/${product_id}`
                );
            }
        });
}
