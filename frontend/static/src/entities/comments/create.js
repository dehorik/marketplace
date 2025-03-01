function createComment(productId, rating, text, photo) {
    // апи запрос на создание отзыва

    const data = new FormData();

    data.append("product_id", productId);
    data.append("rating", rating);
    if (text) data.append("text", text);
    if (photo) data.append("photo", photo);

    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/comments",
                method: "post",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                data: data
            })
                .then(() => {
                    window.location.href = `/products/${productId}`;
                })
                .catch(() => {
                    const errorText = document.querySelector(".comment-form-error-message span");
                    errorText.textContent = "Ошибка создания отзыва";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = `/auth/form?redirect_url=/products/${productId}`;
        });
}
