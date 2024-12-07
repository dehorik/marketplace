const grid = document.querySelector(".comments-grid");


window.addEventListener("load", () => {
    const state = new CommentsLoadingState();
    state.set("product_id", window.location.pathname.split("/").slice(-1)[0]);
    state.set("last_id", null);

    const observer = new MutationObserver((mutations) => {
        if (grid.querySelectorAll(".comment").length <= 10) {
            window.removeEventListener("scroll", check_position);
            setTimeout(() => {
                window.addEventListener("scroll", check_position);
            }, 250);

            get_comments();
        }
    });
    observer.observe(grid, {
        childList: true,
        subtree: true
    });

    window.addEventListener("scroll", check_position);
});


function get_comments() {
    const state = new CommentsLoadingState();

    if (state.is_empty()) {
        return;
    }

    axios({
        url: "/comments/latest",
        method: "get",
        params: {
            product_id: state.get("product_id"),
            amount: 15,
            last_id: state.get("last_id")
        }
    })
        .then((response) => {
            let comments = response.data.comments;

            if (comments.length === 0) {
                state.clear();

                if (!grid.querySelector(".comment") && !grid.querySelector(".comments-message")) {
                    const message_area = document.createElement("div");
                    message_area.className = "comments-message";
                    message_area.textContent = "Отзывы не найдены. Вы можете стать первым, кто оценит товар.";

                    grid.append(message_area);
                }
            }
            else {
                state.set("last_id", comments.slice(-1)[0].comment_id);

                for (let i in comments) {
                    append_comment(comments[i]);
                }
            }
        });
}

function append_comment(comment) {
    const node = create_node(comment);
    grid.append(node);
}

function create_node(comment) {
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

    if (comment.user_id === 2) {
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

        edit_button.addEventListener("click", () => {
            for (let child of document.body.children) {
                child.classList.add("no-display");
            }

            let comment_text_node = node.querySelector(".comment-text");
            let comment_photo_node = node.querySelector(".comment-photo img");

            comment = {
                comment_id: comment.comment_id,
                user_id: comment.user_id,
                product_id: comment.product_id,
                username: comment.username,
                user_photo_path: comment.user_photo_path,
                rating: node.querySelector(".comment-stars").getAttribute("data-rating"),
                creation_date: comment.creation_date,
                text: comment_text_node ? comment_text_node.textContent : null,
                comment_photo_path: comment_photo_node ? comment_photo_node.src : null
            };

            const form = get_form(comment);
            document.body.prepend(form);
        });

        delete_button.addEventListener("click", (event) => {
            delete_comment(node, comment.comment_id);
        });

        node.append(buttons_container);

        node.addEventListener("mouseenter", (event) => {
            const comment_data_container = event.target.querySelector(".comment-data-container");

            if (comment_data_container) {
                const height = event.target.getBoundingClientRect().height;
                const comment_buttons_container = event.target.querySelector(".comment-buttons-container");

                comment_data_container.classList.add("no-display");
                comment_buttons_container.classList.remove("no-display");
                comment_buttons_container.style.height = `${height}px`;
            }
        });

        node.addEventListener("mouseleave", (event) => {
            const comment_data_container = event.target.querySelector(".comment-data-container");

            if (comment_data_container) {
                const comment_buttons_container = event.target.querySelector(".comment-buttons-container");

                comment_buttons_container.classList.add("no-display");
                comment_data_container.classList.remove("no-display");
            }
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

        get_comments();
    }
}


function recalculate_product_rating() {
    const amount_comments_container = document.querySelector(".product_amount-comments span");
    const rating_container = document.querySelector(".product-rating span");
    const star_container = document.querySelector(".product-rating img");

    let amount_comments = 0;
    let total_rating = 0;
    for (let comment of grid.querySelectorAll(".comment")) {
        total_rating += Number(comment.querySelector(".comment-stars").getAttribute("data-rating"));
        amount_comments += 1
    }

    amount_comments_container.textContent = String(amount_comments);

    if (amount_comments !== 0) {
        let rating = (total_rating / amount_comments).toFixed(1);
        rating_container.textContent = String(rating);

        if (rating >= 4) {
            star_container.src = "/static/img/active_star.png";
        }
        else {
            star_container.src = "/static/img/inactive_star.png";
        }
    }
    else {
        rating_container.textContent = "0.0";
        star_container.src = "/static/img/inactive_star.png";
    }
}
