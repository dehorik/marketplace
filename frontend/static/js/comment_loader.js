const grid = document.querySelector(".comments-grid");


window.addEventListener("load", () => {
    State.deleteFromStorage();
    const state = new State();
    state.set("user_id", 2)
    state.set("product_id", window.location.pathname.split("/").slice(-1)[0]);
    state.set("last_id", null);

    window.addEventListener("scroll", check_position);
});

function get_comments(amount = 15) {
    const state = new State();

    if (Object.keys(state.data).length === 0) {
        return;
    }

    let url = "/comments/latest";
    let params = {
        product_id: state.get("product_id"),
        amount: amount,
        last_id: state.get("last_id")
    };

    axios.get(url, {params})
        .then((response) => {
            let comments = response.data.comments;

            if (comments.length === 0) {
                State.deleteFromStorage();

                if (!grid.querySelector(".comment")) {
                    get_message();
                }

                return;
            }

            state.set("last_id", comments.slice(-1)[0].comment_id);

            for (let i in comments) {
                append(comments[i]);
            }
        });
}

function get_message() {
    if (grid.querySelector(".comments-message")) {
        return;
    }

    const message_area = document.createElement("div");
    message_area.className = "comments-message";
    message_area.textContent = "Отзывы не найдены. Вы можете стать первым, кто оценит товар.";
    grid.append(message_area);
}

function append(comment) {
    comment = create_node(comment);
    grid.append(comment);
}

function create_node(comment) {
    const state = new State();

    const node = document.createElement("div");
    node.className = "comment";
    node.id = `comment${comment.comment_id}`;

    const data_container = document.createElement("div");
    data_container.className = "comment-data-container";
    const head = document.createElement("div");
    const user_photo_container = document.createElement("div");
    const user_photo = document.createElement("img");
    const username = document.createElement("div");
    const date = document.createElement("div");
    const stars = document.createElement("div");
    head.className = "comment-head";
    user_photo_container.className = "comment-user-photo";
    user_photo.src = comment.user_photo_path ? `/${comment.user_photo_path}` : "/static/img/default-avatar.png";
    user_photo.alt = "user";
    username.className = "comment-username";
    username.textContent = comment.username;
    date.className = "comment-date";
    date.textContent = comment.creation_date.split()[0].split("T")[0].split("-").reverse().join(".");
    stars.className = "comment-stars";

    user_photo_container.append(user_photo);

    for (let i = 1; i < 6; i++) {
        const star_img = document.createElement("img");

        if (comment.rating >= i) {
            star_img.src = "/static/img/active_star.png";
        } else {
            star_img.src = "/static/img/inactive_star.png";
        }
        star_img.alt = "star";
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

    if (2 === comment.user_id) {
        const buttons_container = document.createElement("div");
        buttons_container.classList.add("comment-buttons-container", "no-display");
        const edit_comment_link = document.createElement("a");
        const delete_comment_link = document.createElement("a");
        const edit_comment_text = document.createElement("span");
        const delete_comment_text = document.createElement("span");
        edit_comment_text.textContent = "Изменить отзыв";
        delete_comment_text.textContent = "Удалить отзыв";
        edit_comment_link.append(edit_comment_text);
        delete_comment_link.append(delete_comment_text);
        buttons_container.append(edit_comment_link);
        buttons_container.append(delete_comment_link);

        delete_comment_link.addEventListener("click", () => {
            delete_comment(node, comment.comment_id);
        })

        node.append(buttons_container);

        node.addEventListener("mouseenter", (event) => {
            show_buttons(event.target);
        });

        node.addEventListener("mouseleave", (event) => {
            hide_buttons(event.target);
        });
    }

    return node;
}

function check_position() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 120) {
        get_comments(15);
    }
}
