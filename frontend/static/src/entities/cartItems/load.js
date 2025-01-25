function getCartItems() {
    const state = new State();

    if (!state.isEmpty()) {
        getVerifiedToken()
            .then((token) => {
                axios({
                    url: "/cart-items/latest",
                    method: "get",
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    params: {
                        amount: 15,
                        last_id: state.get("last_id")
                    }
                })
                    .then((response) => {
                        let cartItems = response.data.cart_items;

                        if (cartItems.length === 0) {
                            state.clear();

                            if (!cartItemsGrid.querySelector(".cart-item_container")) {
                                appendCartItemsNotFoundMessage();
                            }
                        }
                        else {
                            state.set("last_id", cartItems.slice(-1)[0].cart_item_id);

                            for (let item of cartItems) {
                                appendCartItem(item);
                            }
                        }
                    })
                    .catch(() => {
                        if (!cartItemsGrid.querySelector(".cart-item_container")) {
                            appendCartItemsNotFoundMessage();
                        }
                    });
            })
            .catch(() => {
                deleteToken();
                window.location.href = "/auth/form?redirect_url=/cart-items";
            });
    }
}

function appendCartItem(cartItem) {
    cartItemsGrid.appendChild(createCartItemNode(cartItem));
}

function createCartItemNode(cartItem) {
    const container = document.createElement("div");
    container.className = "cart-item_container";
    container.setAttribute("data-product-id", cartItem.product_id);

    if (cartItem.cart_item_id) {
        container.setAttribute("data-cart-item-id", cartItem.cart_item_id);
    }

    const photoContainer = document.createElement('div');
    const photoLink = document.createElement("a");
    const photo = document.createElement("img");
    photoContainer.className = "cart-item_photo-container";
    photoLink.href = `/products/${cartItem.product_id}`;
    photo.src = cartItem.product_photo_path;
    photoLink.appendChild(photo);
    photoContainer.appendChild(photoLink);

    const textData = document.createElement("div");
    textData.className = "cart-item_text-data";

    const nameContainer = document.createElement("div");
    const nameLink = document.createElement("a");
    const name = document.createElement("span");
    nameContainer.className = "cart-item_name";
    nameLink.href = `/products/${cartItem.product_id}`;
    name.textContent = cartItem.product_name;
    nameLink.appendChild(name);
    nameContainer.appendChild(nameLink);

    const priceContainer = document.createElement("div");
    const price = document.createElement("span");
    priceContainer.className = "cart-item_price";
    price.textContent = `${cartItem.product_price} $`;
    priceContainer.appendChild(price);

    textData.appendChild(nameContainer);
    textData.appendChild(priceContainer);

    const buttonsContainer = document.createElement("div")
    const buttons = document.createElement("div");
    buttonsContainer.className = "cart-item_buttons-container";
    buttons.className = "cart-item_buttons";

    const buyBtn = document.createElement("div");
    const buyBtnText = document.createElement("span");
    buyBtnText.textContent = "Купить товар";
    buyBtn.appendChild(buyBtnText);

    const deleteBtn = document.createElement("div");
    const deleteBtnText = document.createElement("span");
    deleteBtnText.textContent = "Удалить из корзины";
    deleteBtn.appendChild(deleteBtnText);

    buttons.appendChild(buyBtn);
    buttons.appendChild(deleteBtn);
    buttonsContainer.appendChild(buttons);

    container.appendChild(photoContainer);
    container.appendChild(textData);
    container.appendChild(buttonsContainer);

    if (getToken()) {
        buyBtn.addEventListener("click", () => {
            appendOrderForm(cartItem);
        })
    }
    else {
        buyBtn.addEventListener("click", () => {
            window.location.href = `/auth/form?redirect_url=/cart-items`;
        })
    }

    if (cartItem.cart_item_id) {
        deleteBtn.addEventListener("click", () => {
            deleteCartItem(container, cartItem.cart_item_id);
        });
    }
    else {
        deleteBtn.addEventListener("click", () => {
            deleteCartItemFromStorage(container, cartItem.product_id);
        });
    }

    return container;
}

function appendCartItemsNotFoundMessage() {
    if (!cartItemsGrid.querySelector(".cart-items-message")) {
        const message = document.createElement("div");
        const messageText = document.createElement("span");
        message.className = "cart-items-message";
        messageText.textContent = "Тут пока пусто!";
        message.appendChild(messageText);

        cartItemsGrid.appendChild(message);
    }
}

function checkPosition() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 220) {
        window.removeEventListener("scroll", checkPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkPosition);
        }, 250);

        getCartItems();
    }
}
