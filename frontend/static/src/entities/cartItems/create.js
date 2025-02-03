function createCartItem(productId) {
    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/cart-items",
                method: "post",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: {
                    product_id: productId
                }
            })
                .then(() => {
                    replaceCartItemBtn();
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = `/auth/form?redirect_url=/products/${productId}`;
        });
}

function createCartItems() {
    let cartItems = JSON.parse(localStorage.getItem("cartItems"));

    if (cartItems) {
        localStorage.removeItem("cartItems");

        for (let item of cartItems) {
            getVerifiedToken().then((token) => {
                axios({
                    url: "/cart-items",
                    method: "post",
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    data: {
                        product_id: item.product_id
                    }
                });
            });
        }
    }
}

function addCartItemToStorage(cartItemCreationBtn, productId, productName, productPrice) {
    let cartItem = {
        product_id: productId,
        product_name: productName,
        product_price: productPrice,
    };

    let cartItems = JSON.parse(localStorage.getItem("cartItems"));

    if (cartItems) {
        cartItems.unshift(cartItem);

        if (cartItems.length > 10) {
            cartItems.splice(10, 1);
        }
    }
    else {
        cartItems = [cartItem];
    }

    localStorage.setItem("cartItems", JSON.stringify(cartItems));
    replaceCartItemBtn();
}

function replaceCartItemBtn() {
    const cartItemsBtn = document.createElement("a");
    const cartItemsBtnText = document.createElement("span");
    cartItemsBtn.className = "product_cart-item-management-button";
    cartItemsBtn.href = "/cart-items";
    cartItemsBtnText.textContent = "Уже в корзине";
    cartItemsBtn.appendChild(cartItemsBtnText);

    const cartItemCreationBtn = document.getElementById("cart-item-creation-button");
    cartItemCreationBtn.parentNode.replaceChild(cartItemsBtn, cartItemCreationBtn);
}
