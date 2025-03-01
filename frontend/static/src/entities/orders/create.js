function createOrder(product_id, address) {
    // апи запрос на создание заказа

    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/orders",
                method: "post",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: {
                    product_id: product_id,
                    delivery_address: address
                }
            })
                .then(() => {
                    window.location.href = "/orders";
                })
                .catch((error) => {
                    const errorText = document.querySelector(".order-creation-form_error span");
                    errorText.textContent = "Ошибка создания заказа";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = `/auth/form?redirect_url=/products/${product_id}`;
        });
}
