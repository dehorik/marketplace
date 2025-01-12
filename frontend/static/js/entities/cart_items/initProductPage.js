window.addEventListener("load", () => {
    const product_id = window.location.pathname.split("/").slice(-1)[0];
    const cart_item_creation_btn = document.getElementById("cart-item-creation-button");

    if (cart_item_creation_btn) {
        if (getToken()) {
            cart_item_creation_btn.addEventListener("click", createCartItem);
        }
        else {
            let cart_items = JSON.parse(localStorage.getItem("cart_items"));

            if (cart_items) {
                for (let i = 0; i < cart_items.length; i++) {
                    if (cart_items[i].product_id === product_id) {
                        cart_item_creation_btn.removeAttribute("id");
                        cart_item_creation_btn.href = "/cart-items";

                        const cart_item_creation_btn_text = cart_item_creation_btn.querySelector("span");
                        cart_item_creation_btn_text.textContent = "Уже в корзине";

                        return;
                    }
                }
            }

            cart_item_creation_btn.addEventListener("click", addCartItemToStorage);
        }
    }
});
