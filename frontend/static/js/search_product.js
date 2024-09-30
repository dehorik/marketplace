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
        window.location.href = "/products";
        return;
    }

    if (document.getElementById("not-found-message")) {
        document.getElementById("not-found-message").remove();
    }

    axios.get("/products/search", {
        params: {
            product_name: input_product_name_elem.value,
            amount: 9
        }
    })
        .then(function (response) {
            const grid = document.body.querySelector("#grid");
            grid.innerHTML = "";

            localStorage.setItem("state", "searching");
            localStorage.setItem("searched-product-name", input_product_name_elem.value);

            let products = response.data.products;

            if (products.length === 0) {
                if (document.getElementById("not-found-message")) {
                    return;
                }

                const message = document.createElement("div");
                message.innerHTML = "Ничего не найдено!";
                message.id = "not-found-message";
                grid.after(message)
            }

            for (let i in products) {
                const product = products[i];
                const item = create_item(product);
                place_item(item);
            }
        });
});
