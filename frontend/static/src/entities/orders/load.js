function getOrders() {
    const state = new State();

    if (!state.isEmpty()) {
        getVerifiedToken()
            .then((token) => {
                axios({
                    url: "/orders/latest",
                    method: "get",
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    params: {
                        amount: 15,
                        last_id: state.get("last_id")
                    }
                })
                    .then((response) => {
                        let orders = response.data.orders;

                        if (orders.length === 0) {
                            state.clear();

                            if (!ordersGrid.querySelector(".order-container")) {
                                appendOrdersNotFoundMessage();
                            }
                        }
                        else {
                            state.set("last_id", orders.slice(-1)[0].order_id);

                            for (let order of orders) {
                                appendOrder(order);
                            }
                        }
                    })
                    .catch(() => {
                        if (!ordersGrid.querySelector(".order-container")) {
                            appendOrdersNotFoundMessage();
                        }
                    });
            })
            .catch(() => {
                deleteToken();
                window.location.href = "/auth/form?redirect_url=/orders";
            });
    }
}

function appendOrder(order) {
    ordersGrid.appendChild(createOrderNode(order));
}

function createOrderNode(order) {
    const currentDate = new Date(Date.UTC(
        new Date().getUTCFullYear(),
        new Date().getUTCMonth(),
        new Date().getUTCDate()
    ));
    const orderDateEnd = new Date(order.date_end + "T00:00:00Z");

    const container = document.createElement("div");
    container.className = "order-container";

    const photoContainer = document.createElement("div");
    const photoLink = document.createElement("a");
    const photo = document.createElement("img");
    photoContainer.className = "order_photo-container";
    photoLink.href = `/products/${order.product_id}`;
    photo.src = `/images/orders/${order.order_id}.jpg?reload=${Date.now()}`;
    photoLink.appendChild(photo);
    photoContainer.appendChild(photoLink);
    container.appendChild(photoContainer);

    const textDataContainer = document.createElement("div");
    textDataContainer.className = "order_text-data-container";
    container.appendChild(textDataContainer);

    const productNameContainer = document.createElement("div");
    const productNameLink = document.createElement("a");
    const productName = document.createElement("span");
    productNameContainer.className = "order_product-name-container";
    productNameLink.href = `/products/${order.product_id}`;
    productName.textContent = order.product_name;
    productNameLink.appendChild(productName);
    productNameContainer.appendChild(productNameLink);

    const productPriceContainer = document.createElement("div");
    const productPrice = document.createElement("span");
    productPriceContainer.className = "order_product-price-container";
    productPrice.textContent = `${order.product_price} $`;
    productPriceContainer.appendChild(productPrice);

    const dateEndContainer = document.createElement("div");
    const dateEndText = document.createElement("span");
    const dateEnd = document.createElement("span");
    dateEndContainer.className = "order_date-end-container";
    dateEndText.textContent = currentDate.getTime() < orderDateEnd.getTime() ? "Будет доставлен: " : "Был доставлен: ";
    dateEnd.textContent = order.date_end.split("-").reverse().join(".");
    dateEndText.appendChild(dateEnd);
    dateEndContainer.appendChild(dateEndText);

    const addressContainer = document.createElement("div");
    const addressText = document.createElement("span");
    const address = document.createElement("span");
    addressContainer.className = "order_address-container";
    addressText.textContent = "Aдрес: ";
    address.textContent = order.delivery_address;
    addressText.appendChild(address);
    addressContainer.appendChild(addressText);

    textDataContainer.appendChild(productNameContainer);
    textDataContainer.appendChild(productPriceContainer);
    textDataContainer.appendChild(dateEndContainer);
    textDataContainer.appendChild(addressContainer);

    const buttonsContainer = document.createElement("div");
    const buttons = document.createElement("div");
    buttonsContainer.className = "order_buttons-container";
    buttons.className = "order_buttons";
    buttonsContainer.appendChild(buttons);
    container.appendChild(buttonsContainer);

    if (currentDate.getTime() < orderDateEnd.getTime()) {
        const updateButtonContainer = document.createElement("div");
        const updateButton = document.createElement("a");
        const updateButtonText = document.createElement("span");
        updateButtonContainer.className = "order_button-container";
        updateButton.className = "order_button";
        updateButtonText.textContent = "Изменить адрес";
        updateButton.appendChild(updateButtonText);
        updateButtonContainer.appendChild(updateButton);
        buttons.appendChild(updateButtonContainer);

        const formContainer = document.createElement("div");
        formContainer.classList.add("order-update-form-container", "no-display");

        const form = document.createElement("div");
        form.className = "order-update-form";

        const addressLabel = document.createElement("label");
        const addressLabelText = document.createElement("span");
        addressLabel.htmlFor = "order-update-form-address-input";
        addressLabelText.textContent = "Введите новый адрес:";
        addressLabel.appendChild(addressLabelText);

        const addressInput = document.createElement("input");
        addressInput.id = "order-update-form-address-input";
        addressInput.type = "text";

        const formButtonsContainer = document.createElement("div");
        formButtonsContainer.className = "order-update-form-buttons-container";

        const submitButtonContainer = document.createElement("div");
        const submitButton = document.createElement("a");
        const submitButtonText = document.createElement("span");
        submitButtonContainer.className = "order-update-form-button-container";
        submitButtonText.textContent = "Сохранить";
        submitButton.appendChild(submitButtonText);
        submitButtonContainer.appendChild(submitButton);

        const cancelButtonContainer = document.createElement("div");
        const cancelButton = document.createElement("a");
        const cancelButtonText = document.createElement("span");
        cancelButtonContainer.className = "order-update-form-button-container";
        cancelButtonText.textContent = "Отменить";
        cancelButton.appendChild(cancelButtonText);
        cancelButtonContainer.appendChild(cancelButton);

        formButtonsContainer.appendChild(submitButtonContainer);
        formButtonsContainer.appendChild(cancelButtonContainer);

        form.appendChild(addressLabel);
        form.appendChild(addressInput);
        form.appendChild(formButtonsContainer);

        const error = document.createElement("div");
        const errorText = document.createElement("span");
        error.className = "order-update-error-container";
        error.appendChild(errorText);

        formContainer.appendChild(form);
        formContainer.appendChild(error);

        container.appendChild(formContainer);

        updateButton.addEventListener("click", () => {
            showUpdateForm(container);
        });

        addressInput.addEventListener("input", (event) => {
            checkAddress(6, 30, event.target.value.trim(), errorText);
        });

        submitButton.addEventListener("click", () => {
            if (addressInput.value.trim() === address.textContent) {
                hideUpdateForm(container);
            }
            else if (checkAddress(6, 30, addressInput.value.trim(), errorText)) {
                updateOrder(order.order_id, addressInput.value.trim(), container);
            }
        });

        cancelButton.addEventListener("click", () => {
            hideUpdateForm(container);
        });
    }
    else {
        const completeButtonContainer = document.createElement("div");
        const completeButton = document.createElement("a");
        const completeButtonText = document.createElement("span");
        completeButtonContainer.className = "order_button-container";
        completeButton.className = "order_button";
        completeButtonText.textContent = "Товар получен";
        completeButton.appendChild(completeButtonText);
        completeButtonContainer.appendChild(completeButton);
        buttons.appendChild(completeButtonContainer);

        completeButton.addEventListener("click", () => {
            deleteOrder(order.order_id, container);
        })
    }

    const deleteButtonContainer = document.createElement("div");
    const deleteButton = document.createElement("a");
    const deleteButtonText = document.createElement("span");
    deleteButtonContainer.className = "order_button-container";
    deleteButton.className = "order_button";
    deleteButtonText.textContent = "Отменить заказ";
    deleteButton.appendChild(deleteButtonText);
    deleteButtonContainer.appendChild(deleteButton);
    buttons.appendChild(deleteButtonContainer);

    deleteButton.addEventListener("click", () => {
        deleteOrder(order.order_id, container);
    });

    return container;
}

function showUpdateForm(node) {
    const photoContainer = node.querySelector(".order_photo-container");
    const textDataContainer = node.querySelector(".order_text-data-container");
    const buttonsContainer = node.querySelector(".order_buttons-container");
    photoContainer.classList.add("no-display");
    textDataContainer.classList.add("no-display");
    buttonsContainer.classList.add("no-display");

    const formContainer = node.querySelector(".order-update-form-container");
    const addressInput = document.getElementById("order-update-form-address-input");
    const errorText = node.querySelector(".order-update-error-container span");
    formContainer.classList.remove("no-display");
    addressInput.value = node.querySelector(".order_address-container span span").textContent;
    errorText.textContent = null;
}

function hideUpdateForm(node) {
    const photoContainer = node.querySelector(".order_photo-container");
    const textDataContainer = node.querySelector(".order_text-data-container");
    const buttonsContainer = node.querySelector(".order_buttons-container");
    photoContainer.classList.remove("no-display");
    textDataContainer.classList.remove("no-display");
    buttonsContainer.classList.remove("no-display");

    const formContainer = node.querySelector(".order-update-form-container");
    const addressInput = document.getElementById("order-update-form-address-input");
    const errorText = node.querySelector(".order-update-error-container span");
    formContainer.classList.add("no-display");
    addressInput.value = null;
    errorText.textContent = null;
}

function checkAddress(ge, le, address, errorText) {
    if (address.length < ge) {
        errorText.textContent = `Недопустимая длина адреса`;
    }
    else if (address.length > le) {
        errorText.textContent = `Недопустимая длина адреса`;
    }
    else {
        errorText.textContent = null;
        return true;
    }
}

function appendOrdersNotFoundMessage() {
    if (!ordersGrid.querySelector(".orders-message")) {
        const message = document.createElement("div");
        const messageText = document.createElement("span");
        message.className = "orders-message";
        messageText.textContent = "Тут пока пусто!";
        message.appendChild(messageText);

        ordersGrid.appendChild(message);
    }
}

function checkPosition() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 220) {
        window.removeEventListener("scroll", checkPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkPosition);
        }, 250);

        getOrders();
    }
}
