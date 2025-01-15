function deleteCartItem(node) {
    node.innerHTML = null;

    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/cart-items/${node.getAttribute("data-cart-item-id")}`,
                method: "delete",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then(() => {
                    node.classList.add("deleted-cart-item");

                    setTimeout(() => {
                        document.querySelector(".cart_grid").removeChild(node);

                        if (!grid.querySelector(".cart-item_container")) {
                            appendCartItemsNotFoundMessage();
                        }
                    }, 1800);
                })
                .catch(() => {
                    node.appendChild(getDeletionError());
                });
        })
        .catch(() => {
            node.appendChild(getDeletionError());
        });
}

function deleteCartItemFromStorage(node) {
    node.innerHTML = null;

    try {
        node.classList.add("deleted-cart-item");

        setTimeout(() => {
            document.querySelector(".cart_grid").removeChild(node);

            if (!grid.querySelector(".cart-item_container")) {
                appendCartItemsNotFoundMessage();
            }
        }, 1800);

        let cart_items = JSON.parse(localStorage.getItem("cart_items"));

        for (let i in cart_items) {
            if (Number(cart_items[i].product_id) === Number(node.getAttribute("data-product-id"))) {
                cart_items.splice(i, 1);
                localStorage.setItem("cart_items", JSON.stringify(cart_items));

                break;
            }
        }
    }
    catch {
        node.appendChild(getDeletionError());
    }
}

function getDeletionError() {
    const error = document.createElement("div");
    const error_text = document.createElement("span");
    error.className = "cart-item-deletion-error";
    error_text.textContent = "Не удалось удалить товар из корзины";
    error.appendChild(error_text);

    return error;
}
