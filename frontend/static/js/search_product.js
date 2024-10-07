const form = document.querySelector(".search form");
const searched_product_name = document.getElementById("search-area");
const warning = document.getElementById("warning");


searched_product_name.addEventListener("input", () => {
    if (searched_product_name.value.length === 0) {
        warning.innerHTML = "";
    }
    else if (searched_product_name.value.length < 2) {
        warning.innerHTML = "Слишком короткое название!";
    }
    else if (searched_product_name.value.length > 20) {
        warning.innerHTML = "Слишком длинное название!";
    }
    else {
        warning.innerHTML = "";
    }
});

form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (searched_product_name.value.length === 0) {
        State.deleteFromStorage();
        const state_data = new CatalogStateData(null);
        const state = new State(state_data);
        state.saveToStorage();

        window.location.href = "/";

        return;
    }
    else if (searched_product_name.value.length < 2) {
        return;
    }
    else if (searched_product_name.value.length > 20) {
        return;
    }

    message_area.innerHTML = "";
    product_grid.innerHTML = "";

    State.deleteFromStorage();
    const state_data = new SearchedProductStateData(searched_product_name.value, null)
    const state = new State(state_data);
    state.saveToStorage();

    update_catalog();
});
