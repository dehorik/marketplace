function getComments() {
    // апи запрос на получение отзывов

    const state = new State();

    if (state.hasProperty("lastCommentId") && state.hasProperty("currentProductId")) {
        axios({
            url: "/comments/latest",
            method: "get",
            params: {
                product_id: state.get("currentProductId"),
                amount: 15,
                last_id: state.get("lastCommentId")
            }
        })
            .then((response) => {
                let comments = response.data.comments;

                if (comments.length === 0) {
                    state.delete("lastCommentId");
                    state.delete("currentProductId");

                    if (!commentsGrid.querySelector(".comment")) {
                        appendCommentsNotFoundMessage(
                            "Отзывы не найдены. Вам нужно заказать товар, чтобы иметь возможность оставить отзыв."
                        );
                    }
                }
                else {
                    state.set("lastCommentId", comments.slice(-1)[0].comment_id);

                    for (let comment of comments) {
                        appendComment(comment);
                    }
                }
            })
            .catch(() => {
                if (!commentsGrid.querySelector(".comment")) {
                    appendCommentsNotFoundMessage("Возникла ошибка во время загрузки отзывов.");
                }
            });
    }
}

function appendComment(comment) {
    // добавление ноды отзыва в сетку

    commentsGrid.append(createCommentNode(comment));
}

function createCommentNode(comment) {
    // создание ноды отзыва

    const container = document.createElement("div");
    container.className = "comment";
    container.setAttribute("data-comment-id", comment.comment_id);

    const dataContainer = document.createElement("div");
    dataContainer.className = "comment-data-container";

    const head = document.createElement("div");
    head.className = "comment-head";

    const userPhotoContainer = document.createElement("div");
    const userPhoto = document.createElement("img");
    userPhotoContainer.className = "comment-user-photo";

    if (comment.user_has_photo) {
        userPhoto.src = `/images/users/${comment.user_id}.jpg?reload=${Date.now()}`;
    }
    else {
        userPhoto.src = "/static/img/default-avatar.png";
    }

    userPhotoContainer.append(userPhoto);

    const username = document.createElement("div");
    username.className = "comment-username";
    username.textContent = comment.username;

    const date = document.createElement("div");
    date.className = "comment-date";
    date.textContent = comment.creation_date.split("-").reverse().join(".");

    const stars = document.createElement("div");
    stars.className = "comment-stars";
    stars.setAttribute("data-rating", comment.rating);

    for (let i = 1; i < 6; i++) {
        const starImg = document.createElement("img");

        if (comment.rating >= i) {
            starImg.src = "/static/img/active-star.png";
        }
        else {
            starImg.src = "/static/img/inactive-star.png";
        }

        stars.append(starImg);
    }

    head.append(userPhotoContainer);
    head.append(username);
    head.append(date);
    head.append(stars);
    dataContainer.append(head);

    if (comment.text) {
        const text = document.createElement("div");
        text.className = "comment-text";
        text.textContent = comment.text;

        dataContainer.append(text);
    }
    if (comment.comment_has_photo) {
        const commentPhotoContainer = document.createElement("div");
        const commentPhoto = document.createElement("img");
        commentPhotoContainer.className = "comment-photo";
        commentPhoto.src = `/images/comments/${comment.comment_id}.jpg?reload=${Date.now()}`;
        commentPhotoContainer.append(commentPhoto);

        dataContainer.append(commentPhotoContainer);
    }

    container.append(dataContainer);

    const token = getToken();

    if (token && comment.user_id === decodeToken(token).sub) {
        // если отзыв принадлежит текущему пользователю - добавляем ему кнопки для управления отзывом

        const buttonsContainer = document.createElement("div");
        buttonsContainer.classList.add("comment-buttons-container", "no-display");

        const editButton = document.createElement("a");
        const editButtonText = document.createElement("span");
        editButtonText.textContent = "Изменить отзыв";
        editButton.append(editButtonText);

        const deleteButton = document.createElement("a");
        const deleteButtonText = document.createElement("span");
        deleteButtonText.textContent = "Удалить отзыв";
        deleteButton.append(deleteButtonText);

        buttonsContainer.append(editButton);
        buttonsContainer.append(deleteButton);

        container.append(buttonsContainer);

        editButton.addEventListener("click", () => {
            appendCommentForm(comment);
        });

        deleteButton.addEventListener("click", () => {
            deleteComment(comment.comment_id, comment.product_id, container);
        });

        container.addEventListener("mouseenter", (event) => {
            showCommentButtons(event);
        });

        container.addEventListener("mouseleave", (event) => {
            hideCommentButtons(event);
        });
    }

    return container;
}

function showCommentButtons(event) {
    // показываем кнопки для управления отзывом

    const dataContainer = event.target.querySelector(".comment-data-container");

    if (dataContainer) {
        const height = event.target.getBoundingClientRect().height;
        const buttonsContainer = event.target.querySelector(".comment-buttons-container");
        const deletionError = event.target.querySelector(".comment-deletion-error");

        dataContainer.classList.add("no-display");

        if (buttonsContainer) {
            buttonsContainer.classList.remove("no-display");
            buttonsContainer.style.height = `${height}px`;
        }
        else {
            deletionError.classList.remove("no-display");
            deletionError.style.height = `${height}px`;
        }
    }
}

function hideCommentButtons(event) {
    // скрываем кнопки для управления отзывом

    const dataContainer = event.target.querySelector(".comment-data-container");

    if (dataContainer) {
        const buttonsContainer = event.target.querySelector(".comment-buttons-container");
        const deletionError = event.target.querySelector(".comment-deletion-error");

        if (buttonsContainer) {
            buttonsContainer.classList.add("no-display");
        }
        else {
            deletionError.classList.add("no-display");
        }

        dataContainer.classList.remove("no-display");
    }
}

function appendCommentsNotFoundMessage(text) {
    // добавляем сообщение, если отзывы не были найдены

    if (!commentsGrid.querySelector(".comments-message")) {
        const message = document.createElement("div");
        message.className = "comments-message";
        message.textContent = text;

        commentsGrid.append(message);
    }
}

function checkCommentsPosition() {
    // отслеживание позиции для дозагрузки отзывов

    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 220) {
        window.removeEventListener("scroll", checkCommentsPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkCommentsPosition);
        }, 250);

        getComments();
    }
}
