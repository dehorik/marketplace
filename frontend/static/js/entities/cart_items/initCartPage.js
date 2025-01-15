const grid = document.querySelector(".cart_grid");


window.addEventListener("load", () => {
    if (getToken()) {
        const state = new State();
        state.clear();
        state.set("last_id", null);

        setTimeout(() => {
            const observer = new MutationObserver(() => {
                if (grid.querySelectorAll(".cart-item_container").length <= 5) {
                    window.removeEventListener("scroll", checkPosition);
                    setTimeout(() => {
                        window.addEventListener("scroll", checkPosition);
                    }, 250);

                    getCartItems();
                }
            });
            observer.observe(grid, {
                childList: true,
                subtree: true
            });

            window.addEventListener("scroll", checkPosition);
        }, 500);

        getCartItems();
    }
    else {
        let cart_items = JSON.parse(localStorage.getItem("cart_items"));

        if (cart_items.length === 0 ) {
            appendCartItemsNotFoundMessage();
        }
        else {
            for (let i in cart_items) {
                appendCartItem(cart_items[i]);
            }
        }
    }
});

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.clear();
});
