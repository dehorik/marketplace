const ordersGrid = document.querySelector(".orders_grid");


window.addEventListener("load", () => {
    initOrders();
});

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.delete("lastOrderId");
});


function initOrders() {
    // инициализация сетки текущих заказов

    if (getToken()) {
        const state = new State();

        state.set("lastOrderId", null);
        getOrders();

        // если слишком много заказов было удалено пользователем - нужно запросить новые
        const observer = new MutationObserver(() => {
            if (ordersGrid.querySelectorAll(".order-container").length <= 5) {
                getOrders();
            }
        });
        observer.observe(ordersGrid, {
            childList: true,
            subtree: true
        });

        setTimeout(() => {
            window.addEventListener("scroll", checkOrdersPosition);
        }, 500);
    }
    else {
        appendOrdersNotFoundMessage(
            "Чтобы просмотреть свои заказы, <a href='/auth/form?redirect_url=/orders'>войдите</a> в аккаунт"
        );
    }
}
