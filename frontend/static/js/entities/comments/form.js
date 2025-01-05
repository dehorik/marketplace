function appendCommentForm(node=null, comment_data=null) {
    for (let child of document.body.children) {
        child.classList.add("no-display");
    }

    if (node && comment_data) {
        const comment_text_node = node.querySelector(".comment-text");
        const comment_photo_node = node.querySelector(".comment-photo img");

        let comment = {
            comment_id: comment_data.comment_id,
            user_id: comment_data.user_id,
            product_id: comment_data.product_id,
            username: comment_data.username,
            user_photo_path: comment_data.user_photo_path,
            rating: node.querySelector(".comment-stars").getAttribute("data-rating"),
            creation_date: node.querySelector(".comment-data-container").textContent,
            text: comment_text_node ? comment_text_node.textContent : null,
            comment_photo_path: comment_photo_node ? comment_photo_node.src : null
        };

        document.body.prepend(getCommentForm(comment));
    }
    else {
        document.body.prepend(getCommentForm());
    }
}

function getCommentForm(comment = null) {
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
            makeStarsActive(event);
        });

        star.setAttribute("data-value", String(i));
        star.alt = "star";

        star_container.appendChild(star);
        rating_stars_container.appendChild(star_container);
    }

    const form = document.createElement("form");
    form.autocomplete = "off";

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

    const upload_button_container = document.createElement("div");
    const upload_button = document.createElement("div");
    const upload_button_text = document.createElement("span");
    const input_elem = document.createElement("input");
    upload_button.className = "comment-form-upload-button";
    upload_button_text.textContent = "Загрузить новое фото";
    input_elem.id = "input-comment-photo";
    input_elem.type = "file";
    input_elem.accept = ".jpg, .png";
    input_elem.className = "no-display";

    upload_button.appendChild(upload_button_text);
    upload_button.appendChild(input_elem);
    upload_button_container.appendChild(upload_button);

    const delete_button_container = document.createElement("div");
    const delete_button = document.createElement("div");
    const delete_button_text = document.createElement("span");
    delete_button.className = "comment-form-delete-button";
    delete_button_text.textContent = "Удалить текущее фото";

    delete_button.appendChild(delete_button_text);
    delete_button_container.appendChild(delete_button);

    photo_buttons.appendChild(upload_button_container);
    photo_buttons.appendChild(delete_button_container);

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

    const error_container = document.createElement("div");
    const error_text = document.createElement("span");
    error_container.className = "comment-form-error-message";
    error_container.appendChild(error_text);
    form.appendChild(error_container);

    const footer = document.createElement("div");
    const footer_text = document.createElement("span");
    footer.className = "comment-form-footer";
    footer_text.innerHTML = "&copy; WebStore";
    footer.appendChild(footer_text);

    container.appendChild(head);
    container.appendChild(rating_stars_container);
    container.appendChild(form);
    container.appendChild(footer);

    cancel_button_img.addEventListener("click", removeForm);

    textarea.addEventListener("input", (event) => {
        checkCommentText(event.target);
    });

    upload_button.addEventListener("click", () => {
        input_elem.click();
    });

    delete_button.addEventListener("click", deleteFile);

    input_elem.addEventListener("change", (event) => {
        uploadFile(event);
    });

    if (comment) {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (checkCommentText(textarea) && checkCommentRating()) {
                updateComment(event.target, comment);
            }
        });
    }
    else {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (checkCommentText(textarea) && checkCommentRating()) {
                createComment(event.target);
            }
        });
    }

    return container;
}

function makeStarsActive(event) {
    const rating_bar = document.querySelectorAll(".comment-form-rating-stars-container a img");
    const rating = Number(event.target.getAttribute("data-value"));
    event.target.parentNode.parentNode.setAttribute("data-rating", String(rating));

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
}

function uploadFile(event) {
    const photo = document.querySelector(".comment-form-photo img");
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = (event) => {
            photo.src = event.target.result;
            photo.setAttribute("data-photo-type", "uploaded");
        };
        reader.readAsDataURL(file);
    }
}

function deleteFile() {
    const photo = document.querySelector(".comment-form-photo img");
    photo.src = "/static/img/empty_photo.png";
    photo.setAttribute("data-photo-type", "default");

    document.getElementById("input-comment-photo").value = null;
}

function checkCommentText(textarea) {
    const error_text = document.querySelector(".comment-form-error-message span");

    if (textarea.value.length > 200) {
        error_text.textContent = "Текст слишком длинный!";
    }
    else if (textarea.value.length < 2 && textarea.value.length !== 0) {
        error_text.textContent = "Текст слишком короткий!";
    }
    else {
        error_text.textContent = null;
        return true;
    }
}

function checkCommentRating() {
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

function removeForm() {
    const form = document.querySelector(".comment-form-container");
    document.body.removeChild(form);

    for (let node of document.body.children) {
        node.classList.remove("no-display");
    }
}
