function appendCommentsNotFoundMessage() {
    if (!grid.querySelector(".comments-message")) {
        const message_area = document.createElement("div");
        message_area.className = "comments-message";
        message_area.textContent = "Отзывы не найдены. Вам нужно заказать товар, чтобы иметь возможность оставить отзыв.";

        grid.append(message_area);
    }
}

function getComments() {
    const state = new State();

    if (!state.isEmpty()) {
        axios({
            url: "/comments/latest",
            method: "get",
            params: {
                product_id: state.get("product_id"),
                amount: 30,
                last_id: state.get("last_id")
            }
        })
            .then((response) => {
                let comments = response.data.comments;

                if (comments.length === 0) {
                    state.clear();

                    if (!grid.querySelector(".comment")) {
                        appendCommentsNotFoundMessage();
                    }
                }
                else {
                    state.set("last_id", comments.slice(-1)[0].comment_id);

                    for (let i in comments) {
                        appendComment(comments[i]);
                    }
                }
            });
    }
}

function appendComment(comment) {
    grid.append(createNode(comment));
}

function createNode(comment) {
    const token = getToken();

    const node = document.createElement("div");
    node.className = "comment";
    node.setAttribute("data-comment-id", comment.comment_id);

    const data_container = document.createElement("div");
    data_container.className = "comment-data-container";

    const head = document.createElement("div");
    head.className = "comment-head";

    const user_photo_container = document.createElement("div");
    const user_photo = document.createElement("img");
    user_photo_container.className = "comment-user-photo";
    user_photo.alt = "user";

    if (comment.user_photo_path) {
        user_photo.src = `/${comment.user_photo_path}`;
    }
    else {
        user_photo.src = "/static/img/default-avatar.png";
    }

    user_photo_container.append(user_photo);

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
        const star_img = document.createElement("img");
        star_img.alt = "star";

        if (comment.rating >= i) {
            star_img.src = "/static/img/active_star.png";
        }
        else {
            star_img.src = "/static/img/inactive_star.png";
        }

        stars.append(star_img);
    }

    head.append(user_photo_container);
    head.append(username);
    head.append(date);
    head.append(stars);
    data_container.append(head);

    if (comment.text) {
        const text = document.createElement("div");
        text.className = "comment-text";
        text.textContent = comment.text;

        data_container.append(text);
    }
    if (comment.comment_photo_path) {
        const comment_photo_container = document.createElement("div");
        const comment_photo = document.createElement("img");
        comment_photo_container.className = "comment-photo";
        comment_photo.src = `/${comment.comment_photo_path}`;
        comment_photo.alt = "photo";
        comment_photo_container.append(comment_photo);

        data_container.append(comment_photo_container);
    }

    node.append(data_container);

    if (token && comment.user_id === decodeToken(token).sub) {
        const buttons_container = document.createElement("div");
        buttons_container.classList.add("comment-buttons-container", "no-display");

        const edit_button = document.createElement("a");
        const edit_button_text = document.createElement("span");
        edit_button_text.textContent = "Изменить отзыв";
        edit_button.append(edit_button_text);

        const delete_button = document.createElement("a");
        const delete_button_text = document.createElement("span");
        delete_button_text.textContent = "Удалить отзыв";
        delete_button.append(delete_button_text);

        buttons_container.append(edit_button);
        buttons_container.append(delete_button);

        node.append(buttons_container);

        edit_button.addEventListener("click", () => {
            appendCommentForm(node, comment);
        });

        delete_button.addEventListener("click", () => {
            deleteComment(node);
        });

        node.addEventListener("mouseenter", (event) => {
            showCommentButtons(event);
        });

        node.addEventListener("mouseleave", (event) => {
            hideCommentButtons(event);
        });
    }

    return node;
}

function showCommentButtons(event) {
    const comment_data_container = event.target.querySelector(".comment-data-container");

    if (comment_data_container) {
        const height = event.target.getBoundingClientRect().height;
        const comment_buttons_container = event.target.querySelector(".comment-buttons-container");
        const comment_deletion_error = event.target.querySelector(".comment-deletion-error");

        comment_data_container.classList.add("no-display");

        if (comment_buttons_container) {
            comment_buttons_container.classList.remove("no-display");
            comment_buttons_container.style.height = `${height}px`;
        }
        else {
            comment_deletion_error.classList.remove("no-display");
            comment_deletion_error.style.height = `${height}px`;
        }
    }
}

function hideCommentButtons(event) {
    const comment_data_container = event.target.querySelector(".comment-data-container");

    if (comment_data_container) {
        const comment_buttons_container = event.target.querySelector(".comment-buttons-container");
        const comment_deletion_error = event.target.querySelector(".comment-deletion-error");

        if (comment_buttons_container) {
            comment_buttons_container.classList.add("no-display");
        }
        else {
            comment_deletion_error.classList.add("no-display");
        }

        comment_data_container.classList.remove("no-display");
    }
}

function checkPosition() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 220) {
        window.removeEventListener("scroll", checkPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkPosition);
        }, 250);

        getComments();
    }
}
