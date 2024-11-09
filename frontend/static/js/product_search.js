const form = document.getElementById("search-form");
const input = document.getElementById("search-area");


form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (input.value.length === 0) {
        location.reload();
    }
    else {
        while (grid.firstChild) {
            grid.removeChild(grid.firstChild);
        }

        State.deleteFromStorage();
        const state = new State();
        state.set("name", input.value);
        state.set("last_id", null);

        get_products(15);
    }
});
