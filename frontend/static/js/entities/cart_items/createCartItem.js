function createCartItem() {
    const cart_item_btn = document.getElementById("cart-item-creation-button");
    cart_item_btn.removeEventListener("click", createCartItem);

    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/cart-items",
                method: "post",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: {
                    product_id: window.location.pathname.split("/").slice(-1)[0]
                }
            })
                .then(() => {
                    cart_item_btn.removeAttribute("id");
                    cart_item_btn.href = "/cart-items";

                    const cart_item_btn_text = cart_item_btn.querySelector("span");
                    cart_item_btn_text.textContent = "Уже в корзине";
                });
        });
}

function createCartItems() {
    let cart_items = JSON.parse(localStorage.getItem("cart_items"));
    localStorage.removeItem("cart_items");

    if (cart_items) {
        for (let i = 0; i < cart_items.length; i++) {
            getVerifiedToken()
                .then((token) => {
                    axios({
                        url: "/cart-items",
                        method: "post",
                        headers: {
                            Authorization: `Bearer ${token}`
                        },
                        data: {
                            product_id: cart_items[i].product_id
                        }
                    });
                });
        }
    }
}

function addCartItemToStorage() {
    const product_id = window.location.pathname.split("/").slice(-1)[0];
    const product_name = document.querySelector(".product-name span").textContent;
    const product_price = document.querySelector(".product-price span").textContent.slice(0, -2);
    const product_photo_path = document.querySelector(".product-photo img").src;

    let cart_item = {
        product_id: product_id,
        product_name: product_name,
        product_price: product_price,
        product_photo_path: product_photo_path
    }

    let cart_items = JSON.parse(localStorage.getItem("cart_items"));

    if (cart_items) {
        cart_items.unshift(cart_item);

        if (cart_items.length > 10) {
            cart_items.splice(10, 1);
        }
    }
    else {
        cart_items = [cart_item];
    }

    localStorage.setItem("cart_items", JSON.stringify(cart_items));

    const cart_item_btn = document.getElementById("cart-item-creation-button");
    const cart_item_btn_text = cart_item_btn.querySelector("span");

    cart_item_btn.removeEventListener("click", addCartItemToStorage);
    cart_item_btn.removeAttribute("id");
    cart_item_btn_text.textContent = "Уже в корзине";
    setTimeout(() => {
        cart_item_btn.href = "/cart-items";
    }, 100);
}
