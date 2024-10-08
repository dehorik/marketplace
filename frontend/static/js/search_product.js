const search_form = document.querySelector(".search-form");
const search_area = document.getElementById("search-area");
const search_warning = document.querySelector(".search-warning");


search_area.addEventListener("input", () => {
    if (search_area.value.length === 0) {
        search_warning.innerHTML = "";
    }
    else if (search_area.value.length < 2) {
        search_warning.innerHTML = "Слишком короткое название!";
    }
    else if (search_area.value.length > 20) {
        search_warning.innerHTML = "Слишком длинное название!";
    }
    else {
        search_warning.innerHTML = "";
    }
});

search_form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (search_area.value.length === 0) {
        State.deleteFromStorage();
        const state_data = new CatalogStateData(null);
        const state = new State(state_data);
        state.saveToStorage();

        window.location.href = "/";

        return;
    }
    else if (search_area.value.length < 2) {
        return;
    }
    else if (search_area.value.length > 20) {
        return;
    }

    message_area.innerHTML = "";
    product_grid.innerHTML = "";

    State.deleteFromStorage();
    const state_data = new SearchedProductStateData(search_area.value, null)
    const state = new State(state_data);
    state.saveToStorage();

    update_catalog();
});
