function getAdminProducts(productsGrid) {
    let state = new State();

    if (!state.isEmpty()) {
        axios({
            url: "/products/latest",
            method: "get",
            params: {
                amount: 30,
                last_id: state.get("last_id")
            }
        })
            .then((response) => {
                let products = response.data.products;

                if (products.length === 0) {
                    state.clear();

                    if (!productsGrid.firstChild) {
                        appendAdminProductsNotFoundMessage();
                    }
                }
                else {
                    deleteAdminProductsNotFoundMessage();
                    state.set("last_id", products.slice(-1)[0].product_id);

                    for (let product of products) {
                        appendAdminProduct(product, productsGrid);
                    }
                }
            });
    }
}

function appendAdminProduct(product, productsGrid) {
    productsGrid.append(createAdminProductNode(product));
}

function createAdminProductNode(product) {
    const container = document.createElement("div");
    container.className = "admin-panel_product-container";

    const node = document.createElement("div");
    node.className = "admin-panel_product";

    const photoContainer = document.createElement("div");
    const photoLink = document.createElement("a");
    const photo = document.createElement("img");
    photoContainer.className = "admin-panel_product-photo-container";
    photoLink.href = `/products/${product.product_id}`;
    photo.src = `/images/products/${product.product_id}.jpg?reload=${Date.now()}`;
    photoLink.appendChild(photo);
    photoContainer.appendChild(photoLink);

    const nameContainer = document.createElement("div");
    const name = document.createElement("a");
    nameContainer.className = "admin-panel_product-name-container";
    name.textContent = product.name;
    name.href = `/products/${product.product_id}`;
    nameContainer.appendChild(name);

    const priceContainer = document.createElement("div");
    const price = document.createElement("span");
    const priceTextData = document.createElement("span");
    priceContainer.className = "admin-panel_product-price-container";
    price.textContent = product.price;
    priceTextData.textContent = "$";
    priceContainer.append(price, priceTextData);

    const buttonsContainer = document.createElement("div");
    buttonsContainer.className = "admin-panel_products-buttons";

    const editingButtonContainer = document.createElement("div");
    const editingButton = document.createElement("a");
    const editingButtonText = document.createElement("span");
    editingButtonText.textContent = "Изменить товар";
    editingButton.appendChild(editingButtonText);
    editingButtonContainer.appendChild(editingButton);

    const deleteButtonContainer = document.createElement("div");
    const deleteButton = document.createElement("a");
    const deleteButtonText = document.createElement("span");
    deleteButtonText.textContent = "Удалить товар";
    deleteButton.appendChild(deleteButtonText);
    deleteButtonContainer.appendChild(deleteButton);

    buttonsContainer.appendChild(editingButtonContainer);
    buttonsContainer.appendChild(deleteButtonContainer);

    node.appendChild(photoContainer);
    node.appendChild(nameContainer);
    node.appendChild(priceContainer);
    node.appendChild(buttonsContainer);
    container.appendChild(node);

    deleteButton.addEventListener("click", () => {
        deleteProduct(product.product_id, container);
    });

    return container;
}

function appendAdminProductsNotFoundMessage() {
    const buttonContainer = document.querySelector(".admin-panel_creation-button-container");

    while (buttonContainer.firstChild) {
        buttonContainer.removeChild(buttonContainer.firstChild);
    }

    const text = document.createElement("span");
    text.textContent = "Товаров пока нет!";

    const button = document.createElement("a");
    const buttonText = document.createElement("span");
    buttonText.textContent = "Создать новый товар?";
    button.appendChild(buttonText);

    buttonContainer.appendChild(text);
    buttonContainer.appendChild(button);
}

function deleteAdminProductsNotFoundMessage() {
    const buttonContainer = document.querySelector(".admin-panel_creation-button-container");

    while (buttonContainer.firstChild) {
        buttonContainer.removeChild(buttonContainer.firstChild);
    }

    const button = document.createElement("a");
    const buttonText = document.createElement("span");
    buttonText.textContent = "Создать новый товар";
    button.appendChild(buttonText);

    buttonContainer.appendChild(button);
}

function checkPosition() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 300) {
        window.removeEventListener("scroll", checkPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkPosition);
        }, 200);

        getAdminProducts(document.querySelector(".admin-panel_products-grid"));
    }
}
