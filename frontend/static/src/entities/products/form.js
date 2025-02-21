function appendProductForm(product=null, productNode=null) {
    for (let node of document.body.children) {
        node.classList.add("no-display");
    }

    document.body.prepend(getProductForm(product, productNode));
}

function deleteProductForm(container) {
    container.remove();

    for (let node of document.body.children) {
        node.classList.remove("no-display");
    }
}

function getProductForm(product=null, productNode=null) {
    const container = document.createElement("div");
    container.className = "product-form-container";

    const node = document.createElement("div");
    node.className = "product-form";

    const title = document.createElement("div");
    title.className = "product-form-title";

    const returnButtonContainer = document.createElement("div");
    const returnButton = document.createElement("a");
    const returnButtonImg = document.createElement("img");
    returnButtonContainer.className = "product-form-title-return-button-container";
    returnButtonImg.src = "/static/img/back.png";
    returnButton.appendChild(returnButtonImg);
    returnButtonContainer.appendChild(returnButton);

    const titleTextContainer = document.createElement("div");
    const titleText = document.createElement("span");
    titleTextContainer.className = "product-form-title-text-container";
    titleText.textContent = product ? "Редактирование товара" : "Создание товара";
    titleTextContainer.appendChild(titleText);

    title.appendChild(returnButtonContainer);
    title.appendChild(titleTextContainer);

    const form = document.createElement("form");
    form.autocomplete = "off";

    const photoNamePriceManagementNode = document.createElement("div");
    photoNamePriceManagementNode.className = "product-form-name-price-photo-management";

    const photoManagementNode = document.createElement("div");
    photoManagementNode.className = "product-form-photo-management";

    const photoContainer = document.createElement("div");
    const photo = document.createElement("img");
    photoContainer.className = "product-form-photo-container";

    if (product) {
        photo.src = `/images/products/${product.product_id}.jpg?reload=${Date.now()}`;
    }
    else {
        photo.src = "/static/img/empty_photo.png";
    }

    photoContainer.appendChild(photo);

    const photoUploadButtonContainer = document.createElement("div");
    const photoUploadButton = document.createElement("a");
    const photoUploadButtonText = document.createElement("span");
    photoUploadButtonContainer.className = "product-form-photo-upload-button-container";
    photoUploadButtonText.textContent = "Загрузить фото";
    photoUploadButton.appendChild(photoUploadButtonText);
    photoUploadButtonContainer.appendChild(photoUploadButton);

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".jpg, .png";
    fileInput.className = "no-display";
    fileInput.id = "input-product-photo";

    photoManagementNode.appendChild(photoContainer);
    photoManagementNode.appendChild(photoUploadButtonContainer);
    photoManagementNode.appendChild(fileInput);

    const namePriceManagementNode = document.createElement("div");
    namePriceManagementNode.className = "product-form-name-price-management";

    const nameManagementNode = document.createElement("div");
    nameManagementNode.className = "product-form-name-management";

    const nameInput = document.createElement("input");
    const nameLabel = document.createElement("label");
    const nameLabelText = document.createElement("span");
    nameInput.id = "product-form-name";
    nameInput.type = "text";
    nameInput.placeholder = "Введите имя товара";
    nameInput.value = product ? product.name : null;
    nameLabel.htmlFor = "product-form-name";
    nameLabelText.textContent = product ? "Подходящее имя товара" : "Введите имя товара";
    nameLabel.appendChild(nameLabelText);
    nameManagementNode.append(nameInput, nameLabel);

    const priceManagementNode = document.createElement("div");
    priceManagementNode.className = "product-form-price-management";

    const priceInput = document.createElement("input");
    const priceTextDataContainer = document.createElement("div");
    const priceTextData = document.createElement("span");
    const priceLabel = document.createElement("label");
    const priceLabelText = document.createElement("span");
    priceInput.id = "product-form-price";
    priceInput.type = "text";
    priceInput.placeholder = "Введите цену товара";
    priceInput.value = product ? product.price : null;
    priceTextData.textContent = "$";
    priceLabel.htmlFor = "product-form-price";
    priceLabelText.textContent = product ? "Подходящая цена товара" : "Введите цену товара";
    priceTextDataContainer.appendChild(priceTextData);
    priceLabel.appendChild(priceLabelText);
    priceManagementNode.append(priceInput, priceTextDataContainer, priceLabel);

    namePriceManagementNode.appendChild(nameManagementNode);
    namePriceManagementNode.appendChild(priceManagementNode);

    photoNamePriceManagementNode.appendChild(photoManagementNode);
    photoNamePriceManagementNode.appendChild(namePriceManagementNode);

    const descriptionManagementNode = document.createElement("div");
    descriptionManagementNode.className = "product-form-description-management";

    const descriptionTextarea = document.createElement("textarea");
    const descriptionLabel = document.createElement("label");
    const descriptionLabelText = document.createElement("span");
    descriptionTextarea.id = "product-form-description";
    descriptionTextarea.maxLength = 405;
    descriptionTextarea.value = product ? product.description : null;
    descriptionLabel.htmlFor = "product-form-description";
    descriptionLabelText.textContent = product ? "Подходящее описание товара" : "Введите описание товара";
    descriptionLabel.appendChild(descriptionLabelText);

    descriptionManagementNode.appendChild(descriptionTextarea);
    descriptionManagementNode.appendChild(descriptionLabel);

    const submitButtonContainer = document.createElement("div");
    const submitButton = document.createElement("button");
    const submitButtonText = document.createElement("span");
    submitButtonContainer.className = "product-form-submit-button-container";
    submitButton.type = "submit";
    submitButtonText.textContent = product ? "Изменить текущий товар" : "Создать новый товар";
    submitButton.appendChild(submitButtonText);
    submitButtonContainer.appendChild(submitButton);

    const errorContainer = document.createElement("div");
    const errorText = document.createElement("span");
    errorContainer.className = "product-form-error-container";
    errorContainer.appendChild(errorText);

    form.appendChild(photoNamePriceManagementNode);
    form.appendChild(descriptionManagementNode);
    form.appendChild(submitButtonContainer);
    form.appendChild(errorContainer);

    const footer = document.createElement("div");
    const footerText = document.createElement("span");
    footer.className = "product-form-footer";
    footerText.innerHTML = "&copy; WebStore";
    footer.appendChild(footerText)

    node.appendChild(title);
    node.appendChild(form);
    node.appendChild(footer);
    container.appendChild(node);

    returnButton.addEventListener("click", () => {
        deleteProductForm(container);
    });

    photoUploadButton.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", (event) => {
        uploadProductPhoto(event, errorText);
    });

    nameInput.addEventListener("input", () => {
        checkProductName(nameInput.value.trim(), nameLabelText, errorText);
    });

    priceInput.addEventListener("input", () => {
        checkProductPrice(priceInput.value.trim(), priceLabelText, errorText);
    });

    descriptionTextarea.addEventListener("input", () => {
        checkProductDescription(descriptionTextarea.value.trim(), descriptionLabelText, errorText);
    });

    if (product) {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (!checkProductName(nameInput.value.trim(), nameLabelText, errorText)) return;
            if (!checkProductPrice(priceInput.value.trim(), priceLabelText, errorText)) return;
            if (!checkProductDescription(descriptionTextarea.value.trim(), descriptionLabelText, errorText)) return;

            let args = [
                product.name !== nameInput.value.trim() ? nameInput.value.trim() : null,
                Number(product.price) !== Number(priceInput.value.trim()) ? priceInput.value.trim() : null,
                product.description !== descriptionTextarea.value.trim() ? descriptionTextarea.value.trim() : null,
                fileInput.files[0] ? fileInput.files[0] : null
            ];

            if (args.some(Boolean)) {
                updateProduct(product.product_id, ...args, event.target, productNode);
            }
            else {
                deleteProductForm(container);
            }
        });
    }
    else {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            if (!checkProductName(nameInput.value.trim(), nameLabelText, errorText)) {
                return;
            }
            if (!checkProductPrice(priceInput.value.trim(), priceLabelText, errorText)) {
                return;
            }
            if (!checkProductDescription(descriptionTextarea.value.trim(), descriptionLabelText, errorText)) {
                return;
            }
            if (!fileInput.files[0]) {
                errorText.textContent = "Загрузите фото товара";
                return;
            }

            createProduct(
                nameInput.value.trim(),
                priceInput.value.trim(),
                descriptionTextarea.value.trim(),
                fileInput.files[0],
                event.target
            );
        });
    }

    return container;
}

function uploadProductPhoto(event, globalErrorText) {
    const photo = document.querySelector(".product-form-photo-container img");
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = (event) => {
            photo.src = event.target.result;
        };
        reader.readAsDataURL(file);

        globalErrorText.textContent = null;
    }
}

function checkProductName(name, errorText, globalErrorText) {
    globalErrorText.textContent = null;

    if ((name.length < 5 || name.length > 30) && name.length !== 0) {
        errorText.textContent = "Имя товара не подходит";
        errorText.parentNode.classList.add("product-form-error-color");
    }
    else if (name.length === 0) {
        errorText.textContent = "Введите имя товара";
        errorText.parentNode.classList.remove("product-form-error-color");
    }
    else {
        errorText.textContent = "Подходящее имя товара";
        errorText.parentNode.classList.remove("product-form-error-color");

        return true;
    }
}

function checkProductPrice(price, errorText, globalErrorText) {
    globalErrorText.textContent = null;

    const intPrice = parseInt(price, 10);

    if (price.length === 0) {
        errorText.textContent = "Введите цену товара";
        errorText.parentNode.classList.remove("product-form-error-color");
    }
    else if (isNaN(intPrice) || !/^\d+$/.test(price)) {
        errorText.textContent = "Цена товара не подходит";
        errorText.parentNode.classList.add("product-form-error-color");
    }
    else if (intPrice <= 0 || intPrice > 100000) {
        errorText.textContent = "Цена товара не подходит";
        errorText.parentNode.classList.add("product-form-error-color");
    }
    else {
        errorText.textContent = "Подходящая цена товара";
        errorText.parentNode.classList.remove("product-form-error-color");

        return true;
    }
}

function checkProductDescription(description, errorText, globalErrorText) {
    globalErrorText.textContent = null;

    if (description.length === 0) {
        errorText.textContent = "Введите описание товара";
        errorText.parentNode.classList.remove("product-form-error-color");
    }
    else if (description.length < 150) {
        errorText.textContent = "Минимальная длина описания товара не достигнута";
        errorText.parentNode.classList.add("product-form-error-color");
    }
    else if (description.length > 300) {
        errorText.textContent = "Превышена максимальная длина описания товара";
        errorText.parentNode.classList.add("product-form-error-color");
    }
    else {
        errorText.textContent = "Подходящее описание товара";
        errorText.parentNode.classList.remove("product-form-error-color");

        return true;
    }
}
