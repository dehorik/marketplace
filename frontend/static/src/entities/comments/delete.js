function deleteComment(commentId, productId, node) {
    // апи запрос на удаление отзыва

    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/comments/${commentId}`,
                method: "delete",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            })
                .then(() => {
                    node.style.height = node.offsetHeight + "px";
                    node.classList.add("deleted-comment");
                    node.innerHTML = null;

                    setTimeout(() => {
                        node.style.height = "0";
                        node.style.margin = "0";
                    }, 10);

                    setTimeout(() => {
                        commentsGrid.removeChild(node);
                        recalculateProductRating();

                        if (commentsGrid.querySelectorAll(".comment").length === 0) {
                            appendCommentsNotFoundMessage(
                                "Отзывы не найдены. Вам нужно заказать товар, чтобы иметь возможность оставить отзыв."
                            );
                        }
                    }, 1610);
                })
                .catch(() => {
                    const error = document.createElement("div");
                    const errorText = document.createElement("span");
                    error.className = "comment-deletion-error";
                    error.style.height = node.offsetHeight + "px";
                    errorText.textContent = "Ошибка удаления отзыва";
                    error.append(errorText);

                    node.querySelector(".comment-buttons-container").replaceWith(error);
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = `/auth/form?redirect_url=/products/${productId}`;
        });
}

function recalculateProductRating() {
    // меняем количество отзывов о товаре и его рейтинг после удаления одного из отзывов пользователем

    const amountCommentsContainer = document.querySelector(".product_amount-comments span");
    const ratingContainer = document.querySelector(".product-rating span");
    const starContainer = document.querySelector(".product-rating img");

    let amountComments = 0;
    let totalRating = 0;
    for (let comment of commentsGrid.querySelectorAll(".comment")) {
        totalRating += Number(comment.querySelector(".comment-stars").getAttribute("data-rating"));
        amountComments += 1;
    }

    amountCommentsContainer.textContent = String(amountComments);

    if (amountComments !== 0) {
        let rating = (totalRating / amountComments).toFixed(1);
        ratingContainer.textContent = String(rating);

        if (rating >= 4) {
            starContainer.src = "/static/img/active-star.png";
        }
        else {
            starContainer.src = "/static/img/inactive-star.png";
        }
    }
    else {
        ratingContainer.textContent = "0.0";
        starContainer.src = "/static/img/inactive-star.png";
    }
}
