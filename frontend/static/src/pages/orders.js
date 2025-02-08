const ordersGrid = document.querySelector(".orders_grid");


window.addEventListener("load", initOrders);

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.clear();
});


function initOrders() {
    if (getToken()) {
        const state = new State();
        state.clear();
        state.set("last_id", null);

        setTimeout(() => {
            const observer = new MutationObserver(() => {
                if (ordersGrid.querySelectorAll(".order-container").length <= 5) {
                    window.removeEventListener("scroll", checkPosition);
                    setTimeout(() => {
                        window.addEventListener("scroll", checkPosition);
                    }, 250);

                    getOrders();
                }
            });
            observer.observe(ordersGrid, {
                childList: true,
                subtree: true
            });

            window.addEventListener("scroll", checkPosition);
        }, 500);

        getOrders();
    }
    else {
        const message = document.createElement("div");
        const messageText = document.createElement("span");
        message.className = "orders-message";
        messageText.innerHTML = "Чтобы просмотреть свои заказы, <a href='/auth/form?redirect_url=/orders'>войдите</a> в аккаунт";
        message.appendChild(messageText);

        ordersGrid.appendChild(message);
    }
}
