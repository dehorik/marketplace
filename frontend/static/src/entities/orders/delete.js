function deleteOrder(orderId, node) {
    // апи запрос на удаление заказа

    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/orders/${orderId}`,
                method: "delete",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then(() => {
                    node.innerHTML = null;
                    node.classList.add("deleted-order-container");

                    setTimeout(() => {
                        ordersGrid.removeChild(node);

                        if (!ordersGrid.querySelector(".order-container")) {
                            appendOrdersNotFoundMessage("Тут пока пусто!");
                        }
                    }, 1800);
                })
                .catch(() => {
                    const error = document.createElement("div");
                    const errorText = document.createElement("span");
                    error.className = "order-deletion-error-container";
                    errorText.textContent = "Не удалось удалить заказ";
                    error.appendChild(errorText);

                    node.innerHTML = null;
                    node.appendChild(error);
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/orders";
        });
}
