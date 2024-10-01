const form = document.querySelector(".search-field form");
const input_product_name_elem = document.getElementById("search-field-area");
const exception_message_elem = document.getElementById("exception-message-area");


function validate_form_data() {
    if (input_product_name_elem.value.length === 0) {
        return true;
    }

    if (input_product_name_elem.value.length < 2) {
        return false;
    }
    else if (input_product_name_elem.value.length > 20) {
        return false;
    }

    return true;
}

input_product_name_elem.addEventListener("input", () => {
    if (input_product_name_elem.value.length === 0) {
        exception_message_elem.innerHTML = "";
    }
    else if (input_product_name_elem.value.length < 2) {
        exception_message_elem.innerHTML = "Слишком короткое название!";
    }
    else if (input_product_name_elem.value.length > 20) {
        exception_message_elem.innerHTML = "Слишком длинное название!";
    }
    else {
        exception_message_elem.innerHTML = "";
    }
});

form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!validate_form_data()) {
        return;
    }

    if (input_product_name_elem.value.length === 0) {
        localStorage.removeItem("searching");
        window.location.href = "/";
        return;
    }

    document.getElementById("not-found-message").innerHTML = "";

    axios.get("/products/search", {
        params: {
            product_name: input_product_name_elem.value,
            amount: 9
        }
    })
        .then(function (response) {
            const grid = document.body.querySelector(".merchants-items");
            grid.innerHTML = "";

            localStorage.setItem("searching", input_product_name_elem.value);

            let products = response.data.products;

            if (products.length === 0) {
                const message_elem = document.getElementById("not-found-message");

                if (message_elem.innerHTML === "") {
                    message_elem.innerHTML = "Ничего не найдено!";
                }
            }

            for (let i in products) {
                const product = products[i];
                const item = create_item(product);
                place_item(item);
            }
        });
});
