window.addEventListener("load", appendUserPage);


function appendUserPage() {
    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/users/me",
                method: "get",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then((response) => {
                    const container = document.querySelector(".user-page_container");

                    while (container.firstChild) {
                        container.removeChild(container.firstChild);
                    }

                    container.appendChild(getUserPageNode(response.data));
                })
                .catch(() => {
                    deleteToken();
                    window.location.href = "/auth/form?redirect_url=/users/me/home";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}

function getUserPageNode(user) {
    const container = document.createElement("div");
    container.className = "user-page";

    const data = document.createElement("div");
    data.className = "user-page_data";

    const photoContainer = document.createElement("div");
    const photo = document.createElement("img");
    photoContainer.className = "user-page_user-photo";
    photoContainer.appendChild(photo);

    if (user.has_photo) {
        photo.src = `/images/users/${user.user_id}.jpg?reload=${Date.now()}`;
    }
    else {
        photo.src = "/static/img/default-avatar.png";
    }

    const textDataContainer = document.createElement("div");
    textDataContainer.className = "user-page_text-data-container";

    const usernameContainer = document.createElement("div");
    const username = document.createElement("span");
    usernameContainer.className = 'user-page_username';
    username.textContent = user.username;
    usernameContainer.appendChild(username);

    const emailContainer = document.createElement("div");
    const email = document.createElement("span");
    emailContainer.className = 'user-page_email';
    email.textContent = user.email ? user.email : "Почта ещё не привязана";
    emailContainer.appendChild(email);

    const registrationDateContainer = document.createElement("div");
    const registrationDate = document.createElement("span");
    registrationDateContainer.className = 'user-page_registration-date';
    registrationDate.textContent = `Дата регистрации: ${user.registration_date.split("-").reverse().join(".")}`;
    registrationDateContainer.appendChild(registrationDate);

    textDataContainer.append(usernameContainer, emailContainer, registrationDateContainer);
    data.append(photoContainer, textDataContainer);

    const dataManagementButtonsContainer = document.createElement("div");
    dataManagementButtonsContainer.className = "user-page_data-management";

    const dataEditingBtnContainer = document.createElement("div");
    const dataEditingBtn = document.createElement("a");
    const dataEditingBtnText = document.createElement("span");
    dataEditingBtnContainer.className = "user-page_data-editing-btn";
    dataEditingBtnText.textContent = "Изменить данные";
    dataEditingBtn.appendChild(dataEditingBtnText);
    dataEditingBtnContainer.appendChild(dataEditingBtn);

    const logoutBtnContainer = document.createElement("div");
    const logoutBtn = document.createElement("a");
    const logoutBtnText = document.createElement("span");
    logoutBtnContainer.className = "user-page_logout-btn";
    logoutBtnText.textContent = "Выйти из аккаунта";
    logoutBtn.appendChild(logoutBtnText);
    logoutBtnContainer.appendChild(logoutBtn);

    const deletionBtnContainer = document.createElement("div");
    const deletionBtn = document.createElement("a");
    const deletionBtnText = document.createElement("span");
    deletionBtnContainer.className = "user-page_account-deletion-btn";
    deletionBtnText.textContent = "Удалить аккаунт";
    deletionBtn.appendChild(deletionBtnText);
    deletionBtnContainer.appendChild(deletionBtn);

    dataManagementButtonsContainer.appendChild(dataEditingBtnContainer);
    dataManagementButtonsContainer.appendChild(logoutBtnContainer);
    dataManagementButtonsContainer.appendChild(deletionBtnContainer);

    const navbar = document.createElement("div");
    navbar.className = "user-page_navbar";

    const catalogBtnContainer = document.createElement("div");
    const catalogBtn = document.createElement("a");
    const catalogBtnText = document.createElement("span");
    catalogBtn.href = "/";
    catalogBtnText.textContent = "Каталог";
    catalogBtn.appendChild(catalogBtnText);
    catalogBtnContainer.appendChild(catalogBtn);

    const cartBtnContainer = document.createElement("div");
    const cartBtn = document.createElement("a");
    const cartBtnText = document.createElement("span");
    cartBtn.href = "/cart-items";
    cartBtnText.textContent = "Корзина";
    cartBtn.appendChild(cartBtnText);
    cartBtnContainer.appendChild(cartBtn);

    const ordersBtnContainer = document.createElement("div");
    const ordersBtn = document.createElement("a");
    const ordersBtnText = document.createElement("span");
    ordersBtn.href = "/orders";
    ordersBtnText.textContent = "Мои заказы";
    ordersBtn.appendChild(ordersBtnText);
    ordersBtnContainer.appendChild(ordersBtn);

    navbar.appendChild(catalogBtnContainer);
    navbar.appendChild(cartBtnContainer);
    navbar.appendChild(ordersBtnContainer);

    if (user.role_id >= 2) {
        const adminBtnContainer = document.createElement("div");
        const adminBtn = document.createElement("a");
        const adminBtnText = document.createElement("span");
        adminBtnText.textContent = "Панель управления";
        adminBtn.appendChild(adminBtnText);
        adminBtnContainer.appendChild(adminBtn);

        adminBtn.addEventListener("click", () => {
            appendAdminPanelNode(user, container.parentNode);
        });

        navbar.appendChild(adminBtnContainer);
    }

    container.appendChild(data);
    container.appendChild(dataManagementButtonsContainer);
    container.appendChild(navbar);

    dataEditingBtn.addEventListener("click", () => {
        appendUserUpdateForm(user);
    });

    deletionBtn.addEventListener("click", () => {
        appendUserDeletionForm(user);
    });

    logoutBtn.addEventListener("click", logout);

    return container;
}

function getAdminPanelNode(user) {
    const container = document.createElement("div");
    container.className = "admin-panel_container";

    const node = document.createElement("div");
    node.className = "admin-panel";

    const buttonsContainer = document.createElement("div");
    buttonsContainer.className = "admin-panel_buttons";

    const accountButton = document.createElement("a");
    const accountButtonText = document.createElement("span");
    accountButton.classList.add("admin-panel_button");
    accountButtonText.textContent = "Аккаунт";
    accountButton.appendChild(accountButtonText);

    const productsButton = document.createElement("a");
    const productsButtonText = document.createElement("span");
    productsButton.classList.add("admin-panel_button", "admin-panel_chosen-button");
    productsButtonText.textContent = "Товары";
    productsButton.appendChild(productsButtonText);

    const adminsButton = document.createElement("a");
    const adminsButtonText = document.createElement("span");
    adminsButton.classList.add("admin-panel_button");
    adminsButtonText.textContent = "Администраторы";
    adminsButton.appendChild(adminsButtonText);

    buttonsContainer.appendChild(accountButton);
    buttonsContainer.appendChild(productsButton);
    buttonsContainer.appendChild(adminsButton);

    node.appendChild(buttonsContainer);
    appendProductsGrid(node);
    container.appendChild(node);

    accountButton.addEventListener("click", () => {
        deleteAdminPanelNode(user, container);
    });

    productsButton.addEventListener("click", () => {
        replaceAdminsWithProducts(node);
    });

    adminsButton.addEventListener("click", () => {
       replaceProductsWithAdmins(node);
    });

    return container;
}

function replaceProductsWithAdmins(node) {
    if (!node.querySelector(".admin-panel_admins-grid")) {
        deleteProductsGrid(node);
        appendAdminsGrid(node);

        const navbarButtons = node.querySelectorAll(".admin-panel_buttons a");
        navbarButtons[1].classList.remove("admin-panel_chosen-button");
        navbarButtons[2].classList.add("admin-panel_chosen-button");
    }
}

function replaceAdminsWithProducts(node) {
    if (!node.querySelector(".admin-panel_products-grid")) {
        deleteAdminsGrid(node);
        appendProductsGrid(node);

        const navbarButtons = node.querySelectorAll(".admin-panel_buttons a");
        navbarButtons[2].classList.remove("admin-panel_chosen-button");
        navbarButtons[1].classList.add("admin-panel_chosen-button");
    }
}

function appendProductsGrid(node) {
    const creationButtonContainer = document.createElement("div");
    const creationButtonContainerText = document.createElement("span");
    const creationButton = document.createElement("a");
    const creationButtonText = document.createElement("span");
    creationButtonContainer.className = "admin-panel_creation-button-container";
    creationButtonContainerText.textContent = "Товаров пока нет!";
    creationButtonText.textContent = "Создать новый товар?";
    creationButton.appendChild(creationButtonText);
    creationButtonContainer.appendChild(creationButtonContainerText);
    creationButtonContainer.appendChild(creationButton);

    const productsGrid = document.createElement("div");
    productsGrid.className = "admin-panel_products-grid";

    node.appendChild(creationButtonContainer);
    node.appendChild(productsGrid);

    const observer = new MutationObserver(() => {
        if (productsGrid.querySelectorAll(".admin-panel_product-container").length <= 30) {
            window.removeEventListener("scroll", checkPosition);
            setTimeout(() => {
                window.addEventListener("scroll", checkPosition);
            }, 250);

            getAdminProducts(productsGrid);
        }
    });
    observer.observe(productsGrid, {
        childList: true,
        subtree: true
    });

    const state = new State();
    state.clear();
    state.set("last_id", null);

    getAdminProducts(productsGrid);

    setTimeout(() => {
        window.addEventListener("scroll", checkPosition);
    }, 400);

    creationButton.addEventListener("click", () => {
        appendProductForm();
    });
}

function deleteProductsGrid(node) {
    const creationButtonContainer = document.querySelector(".admin-panel_creation-button-container");
    const productsGrid = document.querySelector(".admin-panel_products-grid");
    node.removeChild(creationButtonContainer);
    node.removeChild(productsGrid);

    const state = new State();
    state.clear();

    window.removeEventListener("scroll", checkPosition);
}

function appendAdminsGrid(node) {
    const creationButtonContainer = document.createElement("div");
    const creationButton = document.createElement("a");
    const creationButtonText = document.createElement("span");
    creationButtonContainer.className = "admin-panel_creation-button-container";
    creationButtonText.textContent = "Добавить администратора";
    creationButton.appendChild(creationButtonText);
    creationButtonContainer.appendChild(creationButton);

    const adminsGrid = document.createElement("div");
    adminsGrid.className = "admin-panel_admins-grid";

    node.appendChild(creationButtonContainer);
    node.appendChild(adminsGrid);

    getAdmins(adminsGrid);
}

function deleteAdminsGrid(node) {
    const creationButtonContainer = document.querySelector(".admin-panel_creation-button-container");
    const adminsGrid = document.querySelector(".admin-panel_admins-grid");
    node.removeChild(creationButtonContainer);
    node.removeChild(adminsGrid);
}

function appendAdminPanelNode(user, userPageContainer) {
    document.body.replaceChild(getAdminPanelNode(user), userPageContainer);
}

function deleteAdminPanelNode(user, adminPanelNode) {
    const state = new State();
    state.clear();

    window.removeEventListener("scroll", checkPosition);

    const userPageContainer = document.createElement("div");
    userPageContainer.className = "user-page_container";
    userPageContainer.appendChild(getUserPageNode(user));

    document.body.replaceChild(userPageContainer, adminPanelNode);
}
