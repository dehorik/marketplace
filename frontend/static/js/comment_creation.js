const message_area = document.querySelector(".comment-creation-message span");
const rating_bar = document.querySelectorAll(".comment-creation-rating a img");


window.addEventListener("load", () => {
    for (let star of rating_bar) {
        star.addEventListener("click", (event) => {
            make_stars_active_forever(event.target);
        })
    }

    const comment_text =  document.getElementById("comment-creation-text");
    const form = document.querySelector(".comment-creation-form-container form");

    comment_text.addEventListener("input", (event) => {
        check_comment_text(event.target);
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (check_comment_text(comment_text) && check_rating()) {
            create_comment(event.target);
        }
    });
});


function make_stars_active_forever(node) {
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

function get_response_window(text) {
    return `
        <div class="comment-creation-response">
            <div class="comment-creation-response-logo">
                <img src="/static/img/logo.png" alt="logo">
            </div>
        
            <div class="comment-creation-response-status">${text}</div>
        
            <div class="comment-creation-response-footer">Вы будете автоматически перенаправлены</div>
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

function create_comment(form) {
    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJpYXQiOjE3MzI4OTMyMzEsImV4cCI6MTczMjk4MzIzMX0.EfMbZ6bQuDvhJuSiLP0UTBnQDk4OLVEmgLppLCI99Cd8Ibtz_FFSZ1hkWYzFgup2UuaLyCCxNh7FPDBlaFwJUCQdNj9VsP-IBzox_Ty6zjkznOYJ04_UyiSoKMIN_IOENw5ZohGhWv9Zyx0ByfEYfzlTCObIF6Jw5NDTsHkF3QxRb_CNe44ctelgshucyWCtSdfivTzxw9vB5rzKizqocKGuS5hfvZmgwKXDI-tqiBlVo4o4Edvo21nIYW1HOS_iI5RivWhzdrvBPDKB_tG5RrqfmYOKjnkPBS5TKd4O1qlOkVXF17gZlwxOcHvsyGdOz3yh5hnlvq9uwvgt0HVJHA";

    const location = new URL(window.location.href);
    const query_params = new URLSearchParams(location.search);
    const product_id = query_params.get("product_id");

    const data = new FormData();

    const rating = rating_bar[0].parentNode.parentNode.getAttribute("data-rating");
    const text = form.querySelector("#comment-creation-text").value;
    const photo = form.querySelector("#comment-creation-photo").files[0];

    data.append("rating", rating);

    if (text) {
        data.append("text", text);
    }

    if (photo) {
        data.append("photo", photo);
    }

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
            append_response_window("Отзыв успешно создан!", `/products/${product_id}`);
        })
        .catch((response) => {
            if (response.status === 422) {
                message_area.textContent = "Ошибка в введённых данных!";
            }

            else if (response.status === 404) {
                append_response_window("Отзыв не создан: товар или пользователь не существует", `/products/${product_id}`);
            }

            else if (response.status === 401 || response.status === 403) {
                append_response_window("Отзыв не создан: ошибка аутентификации", `/products/${product_id}`);
            }

            else {
                append_response_window("Ошибка создания отзыва", `/products/${product_id}`);
            }
        });
}
