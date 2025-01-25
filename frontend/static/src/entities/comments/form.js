function appendCommentForm(comment=null) {
    while (document.body.firstChild) {
        document.body.removeChild(document.body.firstChild);
    }

    document.body.appendChild(getCommentForm(comment));
}

function getCommentForm(comment=null) {
    const productId = window.location.pathname.split("/").slice(-1)[0];

    const container = document.createElement("div");
    container.className = "comment-form-container";

    const head = document.createElement("div");
    head.className = "comment-form-head";

    const returnBtn = document.createElement("div");
    const returnBtnLink = document.createElement("a");
    const returnBtnImg = document.createElement("img");
    returnBtn.className = "comment-form-cancel-button";
    returnBtnLink.href = `/products/${productId}`;
    returnBtnImg.src = "/static/img/back.png";
    returnBtnLink.appendChild(returnBtnImg);
    returnBtn.appendChild(returnBtnLink);

    const title = document.createElement("div");
    const titleText = document.createElement("span");
    title.className = "comment-form-title";
    titleText.textContent = comment ? "Редактирование отзыва" : "Создание отзыва";
    title.appendChild(titleText);

    head.appendChild(returnBtn);
    head.appendChild(title);

    const ratingStarsContainer = document.createElement("div");
    ratingStarsContainer.className = "comment-form-rating-stars-container";

    if (comment) {
        ratingStarsContainer.setAttribute("data-rating", comment.rating);
    }
    else {
        ratingStarsContainer.setAttribute("data-rating", "1");
    }

    for (let i = 1; i < 6; i++) {
        const starContainer = document.createElement("a");
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
            makeStarsActive(event.target);
        });

        star.setAttribute("data-value", String(i));
        star.alt = "star";

        starContainer.appendChild(star);
        ratingStarsContainer.appendChild(starContainer);
    }

    const form = document.createElement("form");
    form.autocomplete = "off";

    const text = document.createElement("textarea");
    text.id = "comment-form-text";
    text.maxLength = 205;
    text.value = comment ? comment.text : null;

    form.appendChild(text);

    const formPhoto = document.createElement("div");
    formPhoto.className = "comment-form-photo-container";

    const photoContainer = document.createElement("div");
    const photo = document.createElement("img");
    photoContainer.className = "comment-form-photo";
    photo.alt = "photo";

    if (comment) {
        if (comment.comment_photo_path) {
            photo.src = `/${comment.comment_photo_path}`;
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

    photoContainer.appendChild(photo);

    const photoButtons = document.createElement("div");
    photoButtons.className = "comment-form-photo-buttons";

    const uploadButtonContainer = document.createElement("div");
    const uploadButton = document.createElement("div");
    const uploadButtonText = document.createElement("span");
    const fileInput = document.createElement("input");
    uploadButton.className = "comment-form-upload-button";
    uploadButtonText.textContent = "Загрузить новое фото";
    fileInput.id = "input-comment-photo";
    fileInput.type = "file";
    fileInput.accept = ".jpg, .png";
    fileInput.className = "no-display";

    uploadButton.appendChild(uploadButtonText);
    uploadButton.appendChild(fileInput);
    uploadButtonContainer.appendChild(uploadButton);

    const deleteButtonContainer = document.createElement("div");
    const deleteButton = document.createElement("div");
    const deleteButtonText = document.createElement("span");
    deleteButton.className = "comment-form-delete-button";
    deleteButtonText.textContent = "Удалить текущее фото";

    deleteButton.appendChild(deleteButtonText);
    deleteButtonContainer.appendChild(deleteButton);

    photoButtons.appendChild(uploadButtonContainer);
    photoButtons.appendChild(deleteButtonContainer);

    formPhoto.appendChild(photoContainer);
    formPhoto.appendChild(photoButtons);

    const submitButtonContainer = document.createElement("div");
    const submitButton = document.createElement("button");
    submitButtonContainer.className = "comment-form-submit-button-container";
    submitButton.type = "submit";
    submitButton.textContent = comment ? "Изменить отзыв" : "Создать отзыв";
    submitButtonContainer.appendChild(submitButton);

    const error = document.createElement("div");
    const errorText = document.createElement("span");
    error.className = "comment-form-error-message";
    error.appendChild(errorText);

    form.appendChild(text);
    form.appendChild(formPhoto);
    form.appendChild(submitButtonContainer);
    form.appendChild(error);

    const footer = document.createElement("div");
    const footerText = document.createElement("span");
    footer.className = "comment-form-footer";
    footerText.innerHTML = "&copy; WebStore";
    footer.appendChild(footerText);

    container.appendChild(head);
    container.appendChild(ratingStarsContainer);
    container.appendChild(form);
    container.appendChild(footer);

    text.addEventListener("input", (event) => {
        checkCommentText(event.target.value.trim(), errorText);
    });

    uploadButton.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", (event) => {
        uploadFile(event);
    });

    deleteButton.addEventListener("click", deleteFile);

    if (comment) {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            const newRating = ratingStarsContainer.getAttribute("data-rating");
            const newText = text.value;
            const newPhoto = fileInput.files[0];

            if (checkCommentText(text.value.trim(), errorText) && checkCommentRating()) {
                updateComment(
                    productId,
                    comment.comment_id,
                    !!(!text.value && comment.text),
                    !!(photo.getAttribute("data-photo-type") === "default" && comment.comment_photo_path),
                    Number(newRating) !== Number(comment.rating) ? newRating : null,
                    newText.trim() !== comment.text ? newText.trim() : null,
                    newPhoto ? newPhoto : null
                );
            }
        });
    }
    else {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (checkCommentText(text.value.trim(), errorText) && checkCommentRating()) {
                createComment(
                    productId,
                    ratingStarsContainer.getAttribute("data-rating"),
                    text.value.trim(),
                    fileInput.files[0]
                );
            }
        });
    }

    return container;
}

function makeStarsActive(currentStar) {
    const ratingBar = document.querySelectorAll(".comment-form-rating-stars-container a img");
    const rating = Number(currentStar.getAttribute("data-value"));
    currentStar.parentNode.parentNode.setAttribute("data-rating", String(rating));

    if (rating < 5) {
        for (let i = 4; i >= rating; i--) {
            if (ratingBar[i].getAttribute("data-state") === "1") {
                ratingBar[i].src = "/static/img/inactive_star.png";
                ratingBar[i].setAttribute("data-state", "0");
            }
        }
    }
    for (let i = 0; i < rating; i++) {
        if (ratingBar[i].getAttribute("data-state") === "0") {
            ratingBar[i].src = "/static/img/active_star.png";
            ratingBar[i].setAttribute("data-state", "1");
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

function checkCommentText(text, errorText) {
    if (text.length > 200) {
        errorText.textContent = "Текст слишком длинный!";
    }
    else if (text.length < 2 && text.length !== 0) {
        errorText.textContent = "Текст слишком короткий!";
    }
    else {
        errorText.textContent = null;
        return true;
    }
}

function checkCommentRating() {
    const ratingBar = document.querySelectorAll(".comment-form-rating-stars-container a img");
    const rating = Number(ratingBar[0].parentNode.parentNode.getAttribute("data-rating"));

    if (rating > 5 || rating < 1) {
        return false;
    }

    for (let star of ratingBar) {
        if (star.getAttribute("data-state") === "1") {
            return true;
        }
    }

    return false;
}
