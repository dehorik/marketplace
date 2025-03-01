const productsGrid = document.querySelector(".products-grid");


window.addEventListener("load", () => {
    initAuthBtn();
    initProducts();
});

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.delete("lastProductId");
    state.delete("lastSearchedProductId");
    state.delete("searchedProductName");
});


function initAuthBtn() {
    // инициализация ссылки на аккаунт пользователя или на форму для входа в аккаунт

    const btn = document.querySelector(".auth-btn");

    if (getToken()) {
        btn.href = "/users/me/home";
    }
    else {
        btn.href = "/auth/form?redirect_url=/users/me/home";
    }
}

function initProducts() {
    // инициализация сетки товаров на главной странице (в том числе и поиска)

    const state = new State();

    state.set("lastProductId", null);
    getProducts();

    const searchForm = document.getElementById("search-form");
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const productName = document.getElementById("search-input");

        if (productName.value.length === 0) {
            location.reload();
        }
        else {
            while (productsGrid.firstChild) {
                productsGrid.removeChild(productsGrid.firstChild);
            }

            const state = new State();
            state.delete("lastProductId")
            state.set("searchedProductName", productName.value.trim());
            state.set("lastSearchedProductId", null);

            getProducts();
        }
    });

    setTimeout(() => {
        window.addEventListener("scroll", checkProductsPosition);
    }, 500);
}
