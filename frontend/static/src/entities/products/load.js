function getProducts() {
    // апи запрос на получение товаров для подгрузки на главную страницу

    let state = new State();

    if (state.hasProperty("lastProductId")) {
        axios({
            url: "/products/latest",
            method: "get",
            params: {
                amount: 30,
                last_id: state.get("lastProductId")
            }
        })
            .then((response) => {
                let products = response.data.products;

                if (products.length === 0) {
                    state.delete("lastProductId");

                    if (!productsGrid.querySelector(".product-catalog-card")) {
                        appendProductsNotFoundMessage("Ничего не найдено!");
                    }
                }
                else {
                    state.set("lastProductId", products.slice(-1)[0].product_id);

                    for (let product of products) {
                        appendProduct(product);
                    }
                }
            })
            .catch(() => {
                if (!productsGrid.querySelector(".product-catalog-card")) {
                    appendProductsNotFoundMessage("Возникла ошибка во время загрузки товаров");
                }
            });
    }
    else if (state.hasProperty("searchedProductName") && state.hasProperty("lastSearchedProductId")) {
        axios({
            url: "/products/search",
            method: "get",
            params: {
                name: state.get("searchedProductName"),
                amount: 30,
                last_id: state.get("lastSearchedProductId")
            }
        })
            .then((response) => {
                let products = response.data.products;

                if (products.length === 0) {
                    state.delete("lastSearchedProductId");
                    state.delete("searchedProductName");

                    if (!productsGrid.querySelector(".product-catalog-card")) {
                        appendProductsNotFoundMessage("Ничего не найдено!");
                    }
                }
                else {
                    state.set("lastSearchedProductId", products.slice(-1)[0].product_id);

                    for (let product of products) {
                        appendProduct(product);
                    }
                }
            })
            .catch(() => {
                if (!productsGrid.querySelector(".product-catalog-card")) {
                    appendProductsNotFoundMessage("Возникла ошибка во время поиска товара");
                }
            });
    }
}

function getAdminPanelProducts(productsGrid) {
    // апи запрос на получение товаров для подгрузки в панель управления

    let state = new State();

    if (state.hasProperty("adminPanelLastProductId")) {
        axios({
            url: "/products/latest",
            method: "get",
            params: {
                amount: 30,
                last_id: state.get("adminPanelLastProductId")
            }
        })
            .then((response) => {
                let products = response.data.products;

                if (products.length === 0) {
                    state.delete("adminPanelLastProductId");

                    if (!productsGrid.firstChild) {
                        appendAdminPanelProductsNotFoundMessage();
                    }
                }
                else {
                    deleteAdminPanelProductsNotFoundMessage();
                    state.set("adminPanelLastProductId", products.slice(-1)[0].product_id);

                    for (let product of products) {
                        appendAdminPanelProduct(product, productsGrid);
                    }
                }
            });
    }
}

function appendProduct(product) {
    // добавление товара на главную страницу в грид

    productsGrid.append(createProductNode(product));
}

function appendAdminPanelProduct(product, productsGrid) {
    // добавление товара в сетку в панели управления

    productsGrid.append(createAdminPanelProductNode(product));
}

function createProductNode(product) {
    // создание дом элемента карточки товара для добавления на главную страницу

    const productUrl = `/products/${product.product_id}`;

    const container = document.createElement("div");
    container.className = "product-catalog-card";

    const photoContainer = document.createElement("div");
    const photoLink = document.createElement("a");
    const photo = document.createElement("img");
    photoContainer.className = "product-catalog-card-photo";
    photoLink.href = productUrl;
    photo.src = `/images/products/${product.product_id}.jpg?reload=${Date.now()}`;
    photoLink.append(photo);
    photoContainer.append(photoLink);

    const price = document.createElement("div");
    price.className = "product-catalog-card-price";
    price.textContent = `${product.price} $`;

    const nameContainer = document.createElement("div");
    const name = document.createElement("a");
    nameContainer.className = "product-catalog-card-name";
    name.href = productUrl;
    name.textContent = product.name;
    nameContainer.append(name);

    const commentsSummary = document.createElement("div");
    const averageRating = document.createElement("div");
    const starImg = document.createElement("img");
    const rating = document.createElement("span");
    const amountComments = document.createElement("div");
    const commentImg = document.createElement("img");
    const amount = document.createElement("span");
    commentsSummary.className = "product-catalog-card-score";
    averageRating.className = "product-catalog-card-rating";
    starImg.src = product.rating >= 4 ? "/static/img/active-star.png/" : "/static/img/inactive-star.png/";
    rating.textContent = product.rating !== Math.round(product.rating) ? product.rating : `${product.rating}.0`;
    amountComments.className = "product-catalog-card-amount-comments";
    commentImg.src = "/static/img/comment.png";
    amount.textContent = product.amount_comments;
    averageRating.append(starImg);
    averageRating.append(rating);
    amountComments.append(commentImg);
    amountComments.append(amount);
    commentsSummary.append(averageRating);
    commentsSummary.append(amountComments);

    container.append(photoContainer);
    container.append(price);
    container.append(nameContainer);
    container.append(commentsSummary);

    return container;
}

function createAdminPanelProductNode(product) {
    // создание дом элемента карточки товара для добавления в панель управления

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

    editingButton.addEventListener("click", () => {
        appendProductForm(product, container);
    });

    deleteButton.addEventListener("click", () => {
        deleteProduct(product.product_id, container);
    });

    return container;
}

function appendProductsNotFoundMessage(text) {
    // добавление сообщения о том, что товары не найдены (на главную страницу)

    if (!document.querySelector(".index-message")) {
        const message = document.createElement("div");
        message.className = "index-message";
        message.textContent = text;
        productsGrid.append(message);
    }
}

function appendAdminPanelProductsNotFoundMessage() {
    // добавление сообщения о том, что товары не найдены (в панель управления)

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

    button.addEventListener("click", () => {
        appendProductForm();
    });
}

function deleteAdminPanelProductsNotFoundMessage() {
    // удаление сообщения о том, что товары не найдены (из панели управления)

    const buttonContainer = document.querySelector(".admin-panel_creation-button-container");

    while (buttonContainer.firstChild) {
        buttonContainer.removeChild(buttonContainer.firstChild);
    }

    const button = document.createElement("a");
    const buttonText = document.createElement("span");
    buttonText.textContent = "Создать новый товар";
    button.appendChild(buttonText);

    buttonContainer.appendChild(button);

    button.addEventListener("click", () => {
        appendProductForm();
    });
}

function checkProductsPosition() {
    // отслеживание текущей позиции для подгрузки товаров на главную страницу

    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 300) {
        window.removeEventListener("scroll", checkProductsPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkProductsPosition);
        }, 200);

        getProducts();
    }
}

function checkAdminPanelProductsPosition() {
    // отслеживание текущей позиции для подгрузки товаров в панель управления

    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 300) {
        window.removeEventListener("scroll", checkAdminPanelProductsPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkAdminPanelProductsPosition);
        }, 200);

        getAdminPanelProducts(document.querySelector(".admin-panel_products-grid"));
    }
}
