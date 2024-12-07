function get_form(comment=null) {
    const container = document.createElement("div");
    container.className = "comment-form-container";

    const head = document.createElement("div");
    head.className = "comment-form-head";

    const cancel_button = document.createElement("div");
    const cancel_button_img = document.createElement("img");
    cancel_button.className = "comment-form-cancel-button";
    cancel_button_img.src = "/static/img/back.png";
    cancel_button.appendChild(cancel_button_img);

    const title = document.createElement("div");
    const title_text = document.createElement("span");
    title.className = "comment-form-title";
    title_text.textContent = comment ? "Редактирование отзыва" : "Создание отзыва";
    title.appendChild(title_text);

    head.appendChild(cancel_button);
    head.appendChild(title);

    const rating_stars_container = document.createElement("div");
    rating_stars_container.className = "comment-form-rating-stars-container";

    if (comment) {
        rating_stars_container.setAttribute("data-rating", comment.rating);
    }
    else {
        rating_stars_container.setAttribute("data-rating", "1");
    }

    for (let i = 1; i < 6; i++) {
        const star_container = document.createElement("a");
        const star = document.createElement("img");

        if (comment) {
            if (comment.rating >= i) {
                star.src = "/static/img/active_star.png";
                star.setAttribute("data-state", "1");
            }
            else {
                star.src = "/static/img/inactive_star.png";
                star.setAttribute("data-state", "0");
            }
        }
        else {
            star.src = "/static/img/inactive_star.png";
            star.setAttribute("data-state", "0");
        }

        star.addEventListener("click", (event) => {
            const rating_bar = document.querySelectorAll(".comment-form-rating-stars-container a img");
            const rating = Number(event.target.getAttribute("data-value"));
            rating_stars_container.setAttribute("data-rating", String(rating));

            if (rating < 5) {
                for (let i = 4; i >= rating; i--) {
                    if (rating_bar[i].getAttribute("data-state") === "1") {
                        rating_bar[i].src = "/static/img/inactive_star.png";
                        rating_bar[i].setAttribute("data-state", "0");
                    }
                }
            }
            for (let i = 0; i < rating; i++) {
                if (rating_bar[i].getAttribute("data-state") === "0") {
                    rating_bar[i].src = "/static/img/active_star.png";
                    rating_bar[i].setAttribute("data-state", "1");
                }
            }
        });

        star.setAttribute("data-value", String(i));
        star.alt = "star";

        star_container.appendChild(star);
        rating_stars_container.appendChild(star_container);
    }

    const form = document.createElement("form");

    const label = document.createElement("label");
    const textarea = document.createElement("textarea");
    textarea.id = "comment-form-text";
    textarea.maxLength = 205;
    textarea.value = comment ? comment.text : null;
    label.htmlFor = "comment-form-text";

    form.appendChild(label);
    form.appendChild(textarea);

    const form_photo = document.createElement("div");
    form_photo.className = "comment-form-photo-container";

    const photo_container = document.createElement("div");
    const photo = document.createElement("img");
    photo_container.className = "comment-form-photo";
    photo.alt = "photo";

    if (comment) {
        if (comment.comment_photo_path) {
            photo.src = comment.comment_photo_path;
            photo.setAttribute("data-photo-type", "uploaded");
        }
        else {
            photo.src = "/static/img/empty_photo.png";
            photo.setAttribute("data-photo-type", "default");
        }
    }
    else {
        photo.src = "/static/img/empty_photo.png";
        photo.setAttribute("data-photo-type", "default");
    }

    photo_container.appendChild(photo);

    const photo_buttons = document.createElement("div");
    photo_buttons.className = "comment-form-photo-buttons";

    const upload_button = document.createElement("div");
    const upload_button_text = document.createElement("span");
    const input_elem = document.createElement("input");
    upload_button.className = "comment-form-upload-button";
    upload_button_text.textContent = "Загрузить новое фото";
    input_elem.type = "file";
    input_elem.accept = ".jpg, .png";
    input_elem.className = "no-display";

    upload_button.appendChild(upload_button_text);
    upload_button.appendChild(input_elem);

    const delete_button = document.createElement("div");
    const delete_button_text = document.createElement("span");
    delete_button.className = "comment-form-delete-button";
    delete_button_text.textContent = "Удалить текущее фото";

    delete_button.appendChild(delete_button_text);

    photo_buttons.appendChild(upload_button);
    photo_buttons.appendChild(delete_button);

    form_photo.appendChild(photo_container);
    form_photo.appendChild(photo_buttons);
    form.appendChild(form_photo);

    const submit_button_container = document.createElement("div");
    const submit_button = document.createElement("button");
    submit_button_container.className = "comment-form-submit-button-container";
    submit_button.type = "submit";
    submit_button.textContent = comment ? "Изменить отзыв" : "Создать отзыв";

    submit_button_container.appendChild(submit_button);
    form.appendChild(submit_button_container);

    const error_message_container = document.createElement("div");
    const error_message = document.createElement("span");
    error_message_container.className = "comment-form-error-message";
    error_message.innerHTML = "&copy; WebStore 2024";
    error_message_container.appendChild(error_message);

    container.appendChild(head);
    container.appendChild(rating_stars_container);
    container.appendChild(form);
    container.appendChild(error_message_container);

    cancel_button_img.addEventListener("click", () => {
        document.body.removeChild(container);

        for (let node of document.body.children) {
            node.classList.remove("no-display");
        }
    });

    textarea.addEventListener("input", (event) => {
        check_text(event.target);
    });

    upload_button.addEventListener("click", () => {
        input_elem.click();
    });

    input_elem.addEventListener("change", (event) => {
        const file = event.target.files[0];

        if (file) {
            const reader = new FileReader();

            reader.onload = (event) => {
                photo.src = event.target.result;
                photo.setAttribute("data-photo-type", "uploaded");
            };
            reader.readAsDataURL(file);
        }
    });

    delete_button.addEventListener("click", () => {
        input_elem.value = null;
        photo.src = "/static/img/empty_photo.png";
        photo.setAttribute("data-photo-type", "default");
    });

    if (comment) {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (check_text(textarea) && check_rating()) {
                update_comment(event.target, comment);
            }
        });
    }
    else {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (check_text(textarea) && check_rating()) {
                create_comment(event.target);
            }
        });
    }

    return container;
}

function check_text(textarea) {
    const message_area = document.querySelector(".comment-form-error-message span");

    if (textarea.value.length > 200) {
        message_area.textContent = "Текст слишком длинный!";
        return false;
    }
    else if (textarea.value.length < 2 && textarea.value.length !== 0) {
        message_area.textContent = "Текст слишком короткий!";
        return false;
    }
    else {
        message_area.innerHTML = "&copy; WebStore 2024";
        return true;
    }
}

function check_rating() {
    const rating_bar = document.querySelectorAll(".comment-form-rating-stars-container a img");
    const rating = Number(rating_bar[0].parentNode.parentNode.getAttribute("data-rating"));

    if (rating > 5 || rating < 1) {
        return false;
    }

    for (let star of rating_bar) {
        if (star.getAttribute("data-state") === "1") {
            return true;
        }
    }

    return false;
}

function get_response(text) {
    return `
        <div class="comment-operation-response">
            <div class="comment-operation-response-logo">
                <img src="/static/img/logo.png" alt="logo">
            </div>
        
            <div class="comment-operation-response-text ">${text}</div>
        
            <div class="comment-operation-response-footer">Вы будете автоматически перенаправлены</div>
        </div>
    `;
}

function append_response(text) {
    const form = document.querySelector(".comment-form-container");
    document.body.removeChild(form);

    const response = get_response(text);
    document.body.insertAdjacentHTML("afterbegin", response);
}

function redirect_to_product() {
    const response = document.querySelector(".comment-operation-response");
    document.body.removeChild(response);

    for (let node of document.body.children) {
        node.classList.remove("no-display");
    }
}
