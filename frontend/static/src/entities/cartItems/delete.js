function deleteCartItem(cartItemId, node) {
    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/cart-items/${cartItemId}`,
                method: "delete",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then(() => {
                    node.innerHTML = null;
                    node.classList.add("deleted-cart-item");

                    setTimeout(() => {
                        cartItemsGrid.removeChild(node);

                        if (!cartItemsGrid.querySelector(".cart-item_container")) {
                            appendCartItemsNotFoundMessage();
                        }
                    }, 1800);
                })
                .catch(() => {
                    appendCartItemDeletionError(node);
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/cart-items";
        });
}

function deleteCartItemFromStorage(node, productId) {
    try {
        node.innerHTML = null;
        node.classList.add("deleted-cart-item");

        setTimeout(() => {
            document.querySelector(".cart_grid").removeChild(node);

            if (!cartItemsGrid.querySelector(".cart-item_container")) {
                appendCartItemsNotFoundMessage();
            }
        }, 1800);

        let cartItems = JSON.parse(localStorage.getItem("cartItems"));

        for (let i in cartItems) {
            if (Number(cartItems[i].product_id) === Number(productId)) {
                cartItems.splice(i, 1);
                localStorage.setItem("cartItems", JSON.stringify(cartItems));

                break;
            }
        }
    }
    catch {
        appendCartItemDeletionError(node);
    }
}

function appendCartItemDeletionError(node) {
    const error = document.createElement("div");
    const errorText = document.createElement("span");
    error.className = "cart-item-deletion-error";
    errorText.textContent = "Не удалось удалить товар из корзины";
    error.appendChild(errorText);

    node.innerHTML = null;
    node.appendChild(error);
}
