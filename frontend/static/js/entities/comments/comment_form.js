function make_stars_active(node) {
    const rating_bar = document.querySelectorAll(".comment-form-rating-bar a img");
    const rating = Number(node.getAttribute("data-value"));
    node.parentNode.parentNode.setAttribute("data-rating", String(rating));

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

function check_comment_text(node) {
    const message_area = document.querySelector(".comment-form-error-message span");

    if (node.value.length > 200) {
        message_area.textContent = "Текст слишком длинный!";
        return false;
    }
    else if (node.value.length < 2 && node.value.length !== 0) {
        message_area.textContent = "Текст слишком короткий!";
        return false;
    }
    else {
        message_area.innerHTML = "&copy; WebStore 2024";
        return true;
    }
}

function check_rating() {
    const rating_bar = document.querySelectorAll(".comment-form-rating-bar a img");
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

function upload_photo(node) {
    const file = node.files[0];

    if (file) {
        const state = new CommentEditingState();
        state.set("clear_photo", false);

        const preview_photo = document.querySelector(".comment-form-photo img");
        const reader = new FileReader();

        reader.onload = function (event) {
            preview_photo.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }
}

function delete_photo() {
    const state = new CommentEditingState();
    state.set("clear_photo", true);

    const photo_upload_node = document.querySelector(".comment-form-upload-button input");
    const preview_photo = document.querySelector(".comment-form-photo img");

    photo_upload_node.value = null;
    preview_photo.src = "/static/img/empty_photo.png";
}

function get_response_window(text) {
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

function append_response_window(text, redirect_to) {
    while (document.body.firstChild) {
        document.body.removeChild(document.body.firstChild);
    }

    const response_window = get_response_window(text);
    document.body.insertAdjacentHTML("afterbegin", response_window);

    setTimeout(() => {
        window.location.href = redirect_to;
    }, 3000);
}
