const grid = document.querySelector(".comments-grid");


window.addEventListener("load", () => {
    const state = new State();
    state.clearState();
    state.set("product_id", window.location.pathname.split("/").slice(-1)[0]);
    state.set("last_id", null);
    state.set("user_id", 2); // для тестов

    // слушатель на сетку отзывов будет подгружать новые отзывы,
    // если их количество в сетке уменьшается (их удаляют)
    const observer = new MutationObserver((mutations) => {
        if (grid.querySelectorAll(".comment").length <= 10) {
            window.removeEventListener("scroll", check_position);
            setTimeout(() => {
                window.addEventListener("scroll", check_position);
            }, 250);

            get_comments(15);
        }
    });
    observer.observe(grid, {
        childList: true,
        subtree: true
    });

    window.addEventListener("scroll", check_position);
});


function get_comments(amount) {
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
                state.clearState();

                if (!grid.querySelector(".comment")) {
                    get_message();
                }
            }
            else {
                state.set("last_id", comments.slice(-1)[0].comment_id);

                for (let i in comments) {
                    append(comments[i]);
                }
            }
        });
}

function get_message() {
    if (!grid.querySelector(".comments-message")) {
        const message_area = document.createElement("div");
        message_area.className = "comments-message";
        message_area.textContent = "Отзывы не найдены. Вы можете стать первым, кто оценит товар.";
        grid.append(message_area);
    }
}

function append(comment) {
    comment = create_node(comment);
    grid.append(comment);
}

function create_node(comment) {
    const state = new State();

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
    date.textContent = comment.creation_date.split()[0].split("T")[0].split("-").reverse().join(".");

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

    if (Number(state.get("user_id")) === comment.user_id) {
        const buttons_container = document.createElement("div");
        buttons_container.classList.add("comment-buttons-container", "no-display");

        const edit_comment_link = document.createElement("a");
        const edit_comment_text = document.createElement("span");
        edit_comment_text.textContent = "Изменить отзыв";
        edit_comment_link.append(edit_comment_text);

        const delete_comment_link = document.createElement("a");
        const delete_comment_text = document.createElement("span");
        delete_comment_text.textContent = "Удалить отзыв";
        delete_comment_link.append(delete_comment_text);

        buttons_container.append(edit_comment_link);
        buttons_container.append(delete_comment_link);

        delete_comment_link.addEventListener("click", (event) => {
            delete_comment(node, comment.comment_id);
        });

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

    if (documentHeight - (windowHeight + scrollPosition) <= 150) {
        window.removeEventListener("scroll", check_position);
        setTimeout(() => {
            window.addEventListener("scroll", check_position);
        }, 250);

        get_comments(15);
    }
}
