function appendCartItemsNotFoundMessage() {
    if (!grid.querySelector(".cart-items-message")) {
        const message_container = document.createElement("div");
        const message = document.createElement("span");
        message_container.className = "cart-items-message";
        message.textContent = "Тут пока пусто!";
        message_container.appendChild(message);

        grid.appendChild(message_container);
    }
}

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
                        amount: 10,
                        last_id: state.get("last_id")
                    }
                })
                    .then((response) => {
                        let cart_items = response.data.cart_items;

                        if (cart_items.length === 0) {
                            state.clear();

                            if (!grid.querySelector(".cart-item_container")) {
                                appendCartItemsNotFoundMessage();
                            }
                        }
                        else {
                            state.set("last_id", cart_items.slice(-1)[0].cart_item_id);

                            for (let i in cart_items) {
                                appendCartItem(cart_items[i]);
                            }
                        }
                    })
                    .catch(() => {
                        if (!grid.querySelector(".cart-item_container")) {
                            appendCartItemsNotFoundMessage();
                        }
                    });
            })
            .catch(() => {
                if (!grid.querySelector(".cart-item_container")) {
                    appendCartItemsNotFoundMessage();
                }
            });
    }
}

function appendCartItem(cart_item) {
    grid.appendChild(createNode(cart_item));
}

function createNode(cart_item) {
    const container = document.createElement("div");
    container.className = "cart-item_container";
    container.setAttribute("data-product-id", cart_item.product_id);

    if (cart_item.cart_item_id) {
        container.setAttribute("data-cart-item-id", cart_item.cart_item_id);
    }

    const photo_container = document.createElement('div');
    const photo_link = document.createElement("a");
    const photo = document.createElement("img");
    photo_container.className = "cart-item_photo-container";
    photo_link.href = `/products/${cart_item.product_id}`;
    photo.src = cart_item.product_photo_path;
    photo_link.appendChild(photo);
    photo_container.appendChild(photo_link);

    const text_data = document.createElement("div");
    text_data.className = "cart-item_text-data";

    const name_container = document.createElement("div");
    const name_link = document.createElement("a");
    const name = document.createElement("span");
    name_container.className = "cart-item_name";
    name_link.href = `/products/${cart_item.product_id}`;
    name.textContent = cart_item.product_name;
    name_link.appendChild(name);
    name_container.appendChild(name_link);

    const price_container = document.createElement("div");
    const price = document.createElement("span");
    price_container.className = "cart-item_price";
    price.textContent = `${cart_item.product_price} $`;
    price_container.appendChild(price);

    text_data.appendChild(name_container);
    text_data.appendChild(price_container);

    const buttons_container = document.createElement("div")
    const buttons = document.createElement("div");
    buttons_container.className = "cart-item_buttons-container";
    buttons.className = "cart-item_buttons";

    const buy_btn = document.createElement("div");
    const buy_btn_text = document.createElement("span");
    buy_btn_text.textContent = "Купить товар";
    buy_btn.appendChild(buy_btn_text);

    const delete_btn = document.createElement("div");
    const delete_btn_text = document.createElement("span");
    delete_btn_text.textContent = "Удалить из корзины";
    delete_btn.appendChild(delete_btn_text);

    buttons.appendChild(buy_btn);
    buttons.appendChild(delete_btn);
    buttons_container.appendChild(buttons);

    container.appendChild(photo_container);
    container.appendChild(text_data);
    container.appendChild(buttons_container);

    if (cart_item.cart_item_id) {
        delete_btn.addEventListener("click", () => {
           deleteCartItem(container);
        });
    }
    else {
        delete_btn.addEventListener("click", () => {
            deleteCartItemFromStorage(container);
        });
    }

    return container;
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
