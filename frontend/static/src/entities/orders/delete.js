function deleteOrder(orderId, node) {
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
                            appendOrdersNotFoundMessage();
                        }
                    }, 1800);
                })
                .catch(() => {
                    appendOrderDeletionError(node);
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/orders";
        });
}

function appendOrderDeletionError(node) {
    const error = document.createElement("div");
    const errorText = document.createElement("span");
    error.className = "order-deletion-error-container";
    errorText.textContent = "Не удалось удалить заказ";
    error.appendChild(errorText);

    node.innerHTML = null;
    node.appendChild(error);
}
