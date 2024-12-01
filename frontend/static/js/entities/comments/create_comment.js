window.addEventListener("load", () => {
    const rating_bar = document.querySelectorAll(".comment-form-rating-bar a img");
    const form = document.querySelector(".comment-form-container form");
    const textarea = document.getElementById("comment-form-text");
    const photo_upload_button = document.querySelector(".comment-form-upload-button");
    const photo_upload_node = document.querySelector(".comment-form-upload-button input");
    const photo_delete_button = document.querySelector(".comment-form-delete-button");

    for (let star of rating_bar) {
        star.addEventListener("click", function (event) {
            make_stars_active(event.target);
        });
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (check_comment_text(textarea) && check_rating()) {
            create_comment(event.target);
        }
    });

    textarea.addEventListener("input", function (event) {
        check_comment_text(event.target);
    });

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


function create_comment(form) {
    const location = new URL(window.location.href);
    const query_params = new URLSearchParams(location.search);
    const product_id = query_params.get("product_id");

    const data = new FormData();

    const rating_bar = document.querySelector(".comment-form-rating-bar");
    const rating = rating_bar.getAttribute("data-rating");
    const text = form.querySelector("#comment-form-text").value;
    const photo = form.querySelector(".comment-form-upload-button input").files[0];

    data.append("rating", rating);

    if (text) {
        data.append("text", text);
    }

    if (photo) {
        data.append("photo", photo);
    }

    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJpYXQiOjE3MzMwNzE1NDYsImV4cCI6MTczMzE2MTU0Nn0.l4WW1Rh8QdZtVsHAiR_IVZalKk6H3YZlMY4N1ueIt6qZHW02wH-Whh8n4k1sZWqJQHZnUvDIsD-GgQtKxviFMLvXcCUgkFSYjLkQ02LhPxVQ68VFIvaqxLV9fJAzIqEJ4XvsNgRnfvgWLuUdHaPNLe5huXjJpI1jSfddMcZ9DwfsYQuCJi7548wbZHfGRZLRXJhmrSdAC5LqEOdQbSy1G46HGZHIx4uGc4cDTECfmU-YSzhq3bOTfyHh5izId-ZCrM_PV6Ka7Uc-6PwjYEkhhIzEEeMyZXToYoKn-5brxeqJOrJA2ZFEN1XwS7H0Nbswu6BOyb6u8MXFb5UNyLsu-Q";

    axios({
        url: "/comments",
        method: "post",
        params: {
            "product_id": product_id
        },
        headers: {
            "Authorization": `Bearer ${jwt}`
        },
        data: data
    })
        .then(() => {
            append_response_window(
                "Отзыв успешно создан!",
                `/products/${product_id}`
            );
        })
        .catch((response) => {
            if (response.status === 422 || response.status === 415) {
                const message_area = document.querySelector(".comment-form-error-message span");
                message_area.textContent = "Ошибка в введённых данных!";
            }

            else if (response.status === 404) {
                append_response_window(
                    "Отзыв не создан: товар или пользователь не существует",
                    `/products/${product_id}`
                );
            }

            else if (response.status === 401 || response.status === 403) {
                append_response_window(
                    "Отзыв не создан: ошибка аутентификации",
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
