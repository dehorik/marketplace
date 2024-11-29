const form = document.getElementById("search-form");
const input = document.getElementById("search-input");


form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (input.value.length === 0) {
        location.reload();
    }
    else {
        while (grid.firstChild) {
            grid.removeChild(grid.firstChild);
        }

        const state = new State();
        state.clearState();
        state.set("name", input.value);
        state.set("last_id", null);

        get_products(15);
    }
});
