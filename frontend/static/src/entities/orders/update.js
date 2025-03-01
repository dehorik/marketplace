function updateOrder(orderId, address, node) {
    // апи запрос на обновление заказа (изменение адреса доставки)

    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/orders/${orderId}`,
                method: "patch",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: {
                    delivery_address: address
                }
            })
                .then((response) => {
                    const AddressNode = node.querySelector(".order_address-container span span");
                    const DateEndNode = node.querySelector(".order_date-end-container span span");
                    AddressNode.textContent = response.data.delivery_address;
                    DateEndNode.textContent = response.data.date_end.split("-").reverse().join(".");

                    hideUpdateForm(node);
                })
                .catch(() => {
                    const errorText = node.querySelector(".order-update-error-container span");
                    errorText.textContent = "Ошибка изменения адреса доставки";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/orders";
        });
}
