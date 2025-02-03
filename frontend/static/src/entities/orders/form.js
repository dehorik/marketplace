function appendOrderForm(data) {
    while (document.body.firstChild) {
        document.body.removeChild(document.body.firstChild);
    }

    document.body.appendChild(getOrderForm(data));
}

function getOrderForm(data) {
    const container = document.createElement("div");
    container.className = "order-creation-form_container";

    const formContainer = document.createElement("div");
    formContainer.className = "order-creation-form";
    container.appendChild(formContainer);

    const title = document.createElement("div");
    title.className = "order-creation-form_title";

    const returnBtn = document.createElement("div");
    const returnBtnLink = document.createElement("a");
    const returnBtnImg = document.createElement("img");
    returnBtn.className = "order-creation-form_title_return-btn";
    returnBtnLink.href = data.cart_item_id ? "/cart-items" : `/products/${data.product_id}`;
    returnBtnImg.src = "/static/img/back.png";
    returnBtnImg.alt = "back";
    returnBtnLink.appendChild(returnBtnImg);
    returnBtn.appendChild(returnBtnLink);

    const titleTextContainer = document.createElement("div");
    const titleText = document.createElement("span");
    titleTextContainer.className = "order-creation-form_title_text";
    titleText.textContent = "Создание заказа";
    titleTextContainer.appendChild(titleText);

    title.appendChild(returnBtn);
    title.appendChild(titleTextContainer);

    const form = document.createElement("form");
    form.autocomplete = "off";

    const productDataContainer = document.createElement("div");
    productDataContainer.className = "order-creation-form_product-data_container";

    const productPhotoContainer = document.createElement("div");
    const productPhoto = document.createElement("img");
    productPhotoContainer.className = "order-creation-form_photo-container";
    productPhoto.src = `/images/products/${data.product_id}.jpg?reload=${Date.now()}`;
    productPhoto.alt = "product";
    productPhotoContainer.appendChild(productPhoto);

    const productDataWrapper = document.createElement("div");
    const productData = document.createElement("div");
    productDataWrapper.className = "order-creation-form_product-data_wrapper";
    productData.className = "order-creation-form_product-data";
    productDataWrapper.appendChild(productData);

    const productNameContainer = document.createElement("div");
    const productName = document.createElement("span");
    productNameContainer.className = "order-creation-form_product_name";
    productName.textContent = data.product_name;
    productNameContainer.appendChild(productName);
    productData.appendChild(productNameContainer);

    const productPriceContainer = document.createElement("div");
    const productPrice = document.createElement("span");
    productPriceContainer.className = "order-creation-form_product_price";
    productPrice.textContent = `${data.product_price} $`;
    productPriceContainer.appendChild(productPrice);
    productData.appendChild(productPriceContainer);

    productDataContainer.appendChild(productPhotoContainer);
    productDataContainer.appendChild(productDataWrapper);

    const addressContainer = document.createElement("div");
    const addressLabel = document.createElement("label");
    const addressInput = document.createElement("input");
    const addressErrorContainer = document.createElement("div");
    const addressError = document.createElement("span");
    addressContainer.className = "order-creation-form_address_container";
    addressLabel.for = "order-creation-form_address";
    addressInput.id = "order-creation-form_address";
    addressInput.type = "text";
    addressInput.placeholder = "Введите адрес доставки";
    addressErrorContainer.className = "order-creation-form_address_error";
    addressErrorContainer.appendChild(addressError);
    addressContainer.append(addressLabel, addressInput, addressErrorContainer);

    const formErrorContainer = document.createElement("div");
    const formError = document.createElement("span");
    formErrorContainer.className = "order-creation-form_error";
    formErrorContainer.appendChild(formError);

    const submitBtnContainer = document.createElement("div");
    const submitBtn = document.createElement("button");
    submitBtnContainer.className = "order-creation-form_submit-btn_container";
    submitBtn.type = "submit";
    submitBtn.textContent = "Создать заказ";
    submitBtnContainer.appendChild(submitBtn);

    form.appendChild(productDataContainer);
    form.appendChild(addressContainer);
    form.appendChild(formErrorContainer);
    form.appendChild(submitBtnContainer);

    const footer = document.createElement("div");
    const footerText = document.createElement("span");
    footer.className = "order-creation-form_footer";
    footerText.innerHTML = "&copy; WebStore";
    footer.appendChild(footerText);

    formContainer.appendChild(title);
    formContainer.appendChild(form);
    formContainer.appendChild(footer);

    addressInput.addEventListener("input", (event) => {
       checkAddress(6, 30, event.target.value.trim(), addressError);
    });

    form.addEventListener("submit", () => {
        if (checkAddress(6, 30, addressInput.value.trim(), addressError)) {
            createOrder(data.product_id, addressInput.value.trim());
        }
    });

    return container;
}

function checkAddress(ge, le, address, errorText) {
    const globalErrorText = document.querySelector(".order-creation-form_error span");
    globalErrorText.textContent = null;

    if (address.length < ge) {
        errorText.textContent = `Недопустимая длина`;
    }
    else if (address.length > le) {
        errorText.textContent = `Недопустимая длина`;
    }
    else {
        errorText.textContent = null;
        return true;
    }
}
