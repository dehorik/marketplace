function updateComment(productId, commentId, clearText, clearPhoto, rating, text, photo) {
    // апи запрос на изменение отзыва

    const data = new FormData();

    data.append("clear_text", clearText);
    data.append("clear_photo", clearPhoto);
    if (rating) data.append("rating", rating);
    if (text) data.append("text", text);
    if (photo) data.append("photo", photo);

    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/comments/${commentId}`,
                method: "patch",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
                data: data
            })
                .then(() => {
                    window.location.href = `/products/${productId}`;
                })
                .catch(() => {
                    const errorText = document.querySelector(".comment-form-error-message span");
                    errorText.textContent = "Ошибка обновления данных";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = `/auth/form?redirect_url=/products/${productId}`;
        });
}
