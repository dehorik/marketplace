const commentsGrid = document.querySelector(".comments-grid");


window.addEventListener("load", () => {
    initCartItemBtn();
    initOrderBtn();
    initComments();
});

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.delete("lastCommentId");
    state.delete("currentProductId");
});


function initComments() {
    // инициализация отзывов под товаром

    const state = new State();

    state.set("lastCommentId", null);
    state.set("currentProductId", window.location.pathname.split("/").slice(-1)[0]);
    getComments();

    const commentCreationBtn = document.querySelector(".comment-creation-link");
    if (commentCreationBtn) {
        commentCreationBtn.addEventListener("click", () => {
            appendCommentForm();
        });
    }

    // если слишком много отзывов было удалено пользователем - нужно запросить новые
    const observer = new MutationObserver(() => {
        if (commentsGrid.querySelectorAll(".comment").length <= 10) {
            getComments();
        }
    });
    observer.observe(commentsGrid, {
        childList: true,
        subtree: true
    });

    setTimeout(() => {
        window.addEventListener("scroll", checkCommentsPosition);
    }, 500);
}

function initCartItemBtn() {
    // инициализация кнопки для добавления товара в корзину

    const productId = window.location.pathname.split("/").slice(-1)[0];
    const productName = document.querySelector(".product-name span").textContent;
    const productPrice = document.querySelector(".product-price span").textContent.slice(0, -2);

    const cartItemCreationBtn = document.getElementById("cart-item-creation-button");

    if (cartItemCreationBtn) {
        if (getToken()) {
            cartItemCreationBtn.addEventListener("click", (event) => {
                createCartItem(productId);
            });
        }
        else {
            let cartItems = JSON.parse(localStorage.getItem("cart_items"));

            if (cartItems) {
                for (let item of cartItems) {
                    if (item.product_id === productId) {
                        replaceCartItemBtn();
                        return;
                    }
                }
            }

            cartItemCreationBtn.addEventListener("click", (event) => {
                addCartItemToStorage(event.target, productId, productName, productPrice);
            });
        }
    }
}

function initOrderBtn() {
    // инициализация кнопки для быстрого создания заказа

    const productId = window.location.pathname.split("/").slice(-1)[0];
    const btn = document.querySelector(".product_order-creation-button");

    if (getToken()) {
        btn.addEventListener("click", () => {
            const productName = document.querySelector(".product-name span").textContent;
            const productPrice = document.querySelector(".product-price span").textContent.slice(0, -2);
            const productPhotoPath = document.querySelector(".product-photo img").getAttribute("src");

            let data = {
                product_id: productId,
                product_name: productName,
                product_price: productPrice,
                product_photo_path: productPhotoPath
            }

            appendOrderForm(data);
        });
    }
    else {
        btn.addEventListener("click", () => {
            window.location.href = `/auth/form?redirect_url=/products/${productId}`;
        });
    }
}
