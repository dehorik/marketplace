function createCartItem(product_id) {
    const token = getVerifiedToken();

    axios({
        url: "/orders/cart",
        method: "post",
        headers: {
            "Authorization": `Bearer ${token}`
        },
        data: {
            "product_id": product_id
        }
    })
        .then(() => {
            const cart_items_link = document.createElement("div");
            cart_items_link.className = "cart-items-link";
            const link = document.createElement("a");
            link.href = "#";
            const text = document.createElement("span");
            text.textContent = "Уже в корзине";

            link.append(text);
            cart_items_link.append(link);

            document.querySelector(".cart-item-creation-button").replaceWith(cart_items_link);
        })
}
