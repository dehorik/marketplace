const cartItemsGrid = document.querySelector(".cart_grid");


window.addEventListener("load", initCartItems);

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.clear();
});


function initCartItems() {
    if (getToken()) {
        const state = new State();
        state.clear();
        state.set("last_id", null);

        setTimeout(() => {
            const observer = new MutationObserver(() => {
                if (cartItemsGrid.querySelectorAll(".cart-item_container").length <= 5) {
                    window.removeEventListener("scroll", checkPosition);
                    setTimeout(() => {
                        window.addEventListener("scroll", checkPosition);
                    }, 250);

                    getCartItems();
                }
            });
            observer.observe(cartItemsGrid, {
                childList: true,
                subtree: true
            });

            window.addEventListener("scroll", checkPosition);
        }, 500);

        getCartItems();
    }
    else {
        let cartItems = JSON.parse(localStorage.getItem("cartItems"));

        if (cartItems.length === 0 ) {
            appendCartItemsNotFoundMessage();
        }
        else {
            for (let item of cartItems) {
                appendCartItem(item);
            }
        }
    }
}
