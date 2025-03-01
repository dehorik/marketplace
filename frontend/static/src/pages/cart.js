const cartItemsGrid = document.querySelector(".cart_grid");


window.addEventListener("load", () => {
    initCartItems();
});

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.delete("lastCartItemId");
});


function initCartItems() {
    // инициализируем корзину пользователя - добавляем товары из localStorage либо запрашиваем с бэка

    if (getToken()) {
        // запросим с бэка товары в корзине пользователя, если пользователь вошел в аккаунт

        const state = new State();

        state.set("lastCartItemId", null);
        getCartItems();

        // если слишком много товаров было удалено из корзины пользователем - нужно запросить новые
        const observer = new MutationObserver(() => {
            if (cartItemsGrid.querySelectorAll(".cart-item_container").length <= 5) {
                getCartItems();
            }
        });
        observer.observe(cartItemsGrid, {
            childList: true,
            subtree: true
        });

        setTimeout(() => {
            window.addEventListener("scroll", checkCartItemsPosition);
        }, 500);
    }
    else {
        // если пользователь не вошел в аккаунт - загрузим товары из localStorage

        let cartItems = JSON.parse(localStorage.getItem("cartItems"));

        if (!cartItems || cartItems.length === 0) {
            appendCartItemsNotFoundMessage("Тут пока пусто!");
        }
        else {
            for (let item of cartItems) {
                appendCartItem(item);
            }
        }
    }
}
