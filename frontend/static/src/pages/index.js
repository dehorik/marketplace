const productsGrid = document.querySelector(".products-grid");


window.addEventListener("load", () => {
    initAuthBtn();
    initProducts();
});

window.addEventListener("beforeunload", () => {
    const state = new State();
    state.clear();
});


function initAuthBtn() {
    const btn = document.querySelector(".auth-btn");

    if (getToken()) {
        btn.href = "/users/me/home";
    }
    else {
        btn.href = "/auth/form?redirect_url=/users/me/home";
    }
}

function initProducts() {
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
            state.clear();
            state.set("name", productName.value.trim());
            state.set("last_id", null);

            getProducts();
        }
    });

    const state = new State();
    state.clear();
    state.set("last_id", null);

    getProducts();

    setTimeout(() => {
        window.addEventListener("scroll", checkPosition);
    }, 500);
}
