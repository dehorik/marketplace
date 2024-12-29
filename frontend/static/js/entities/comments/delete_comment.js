function deleteComment(node) {
    getVerifiedToken().then((token) => {
        axios({
            url: `/comments/${node.getAttribute("data-comment-id")}`,
            method: "delete",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        })
            .then(() => {
                node.style.height = node.offsetHeight + "px";
                node.classList.add("deleted-comment");

                while (node.firstChild) {
                    node.removeChild(node.firstChild);
                }

                setTimeout(() => {
                    node.style.height = "0";
                    node.style.margin = "0";
                }, 10);

                setTimeout(() => {
                    grid.removeChild(node);
                    recalculateProductRating();

                    if (grid.querySelectorAll(".comment").length === 0) {
                        appendCommentsNotFoundMessage();
                    }
                }, 1610);
            })
            .catch(() => {
                const deletion_error = document.createElement("div");
                const deletion_error_message = document.createElement("span");
                deletion_error.className = "comment-deletion-error";
                deletion_error.style.height = node.offsetHeight + "px";
                deletion_error_message.textContent = "Ошибка удаления отзыва";
                deletion_error.append(deletion_error_message);

                node.querySelector(".comment-buttons-container").replaceWith(deletion_error);
            });
    });
}

function recalculateProductRating() {
    const amount_comments_container = document.querySelector(".product_amount-comments span");
    const rating_container = document.querySelector(".product-rating span");
    const star_container = document.querySelector(".product-rating img");

    let amount_comments = 0;
    let total_rating = 0;
    for (let comment of grid.querySelectorAll(".comment")) {
        total_rating += Number(comment.querySelector(".comment-stars").getAttribute("data-rating"));
        amount_comments += 1;
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
