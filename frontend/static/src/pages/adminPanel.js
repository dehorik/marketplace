function appendAdminPanelNode(user, userPageContainer) {
    // добавляем админ панель (старое содержимое контейнера удаляется)

    document.body.replaceChild(getAdminPanelNode(user), userPageContainer);
}

function deleteAdminPanelNode(user, adminPanelNode) {
    // удаляем панель управления, заменяя ее страницей пользователя

    const state = new State();
    state.delete("adminPanelLastProductId");

    window.removeEventListener("scroll", checkAdminPanelProductsPosition);

    const userPageContainer = document.createElement("div");
    userPageContainer.className = "user-page_container";
    userPageContainer.appendChild(getUserPageNode(user));

    document.body.replaceChild(userPageContainer, adminPanelNode);
}

function getAdminPanelNode(user) {
    // создаем дом узел админ панели + обработчики событий

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

    buttonsContainer.appendChild(accountButton);
    buttonsContainer.appendChild(productsButton);

    if (user.role_id > 2) {
        // только суперюзеры могут изменять список администраторов и суперюзеров

        const adminsButton = document.createElement("a");
        const adminsButtonText = document.createElement("span");
        adminsButton.classList.add("admin-panel_button");
        adminsButtonText.textContent = "Администраторы";
        adminsButton.appendChild(adminsButtonText);

        productsButton.addEventListener("click", () => {
            replaceAdminsWithProducts(node);
        });

        adminsButton.addEventListener("click", () => {
            replaceProductsWithAdmins(node);
        });

        buttonsContainer.appendChild(adminsButton);
    }

    node.appendChild(buttonsContainer);
    appendProductsGrid(node);
    container.appendChild(node);

    accountButton.addEventListener("click", () => {
        deleteAdminPanelNode(user, container);
    });

    return container;
}

function appendProductsGrid(node) {
    // добавляет в админ паель сетку товаров + запрашивает первую партию товаров с бэка

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

    creationButton.addEventListener("click", () => {
        appendProductForm();
    });

    const state = new State();

    state.set("adminPanelLastProductId", null);
    getAdminPanelProducts(productsGrid);

    // если слишком много товаров было удалено пользователем - нужно запросить новые
    const observer = new MutationObserver(() => {
        if (productsGrid.querySelectorAll(".admin-panel_product-container").length <= 30) {
            getAdminPanelProducts(productsGrid);
        }
    });
    observer.observe(productsGrid, {
        childList: true,
        subtree: true
    });

    setTimeout(() => {
        window.addEventListener("scroll", checkAdminPanelProductsPosition);
    }, 500);
}

function deleteProductsGrid(node) {
    // удаляет сетку товаров из админ панели

    const creationButtonContainer = document.querySelector(".admin-panel_creation-button-container");
    const productsGrid = document.querySelector(".admin-panel_products-grid");
    node.removeChild(creationButtonContainer);
    node.removeChild(productsGrid);

    const state = new State();
    state.delete("adminPanelLastProductId");

    window.removeEventListener("scroll", checkAdminPanelProductsPosition);
}

function appendAdminsGrid(node) {
    // добавляет сетку админов в админ панель и запрашивает всех админов и суперюзеров с бэка

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

    creationButton.addEventListener("click", () => {
        appendAdminCreationForm(adminsGrid);
    });
}

function deleteAdminsGrid(node) {
    // удаляет сетку админов

    const creationButtonContainer = document.querySelector(".admin-panel_creation-button-container");
    const adminsGrid = document.querySelector(".admin-panel_admins-grid");
    node.removeChild(creationButtonContainer);
    node.removeChild(adminsGrid);
}

function replaceProductsWithAdmins(node) {
    // заменяет сетку товаров на сетку админов

    if (!node.querySelector(".admin-panel_admins-grid")) {
        deleteProductsGrid(node);
        appendAdminsGrid(node);

        const navbarButtons = node.querySelectorAll(".admin-panel_buttons a");
        navbarButtons[1].classList.remove("admin-panel_chosen-button");
        navbarButtons[2].classList.add("admin-panel_chosen-button");
    }
}

function replaceAdminsWithProducts(node) {
    // заменяет сетку админов на сетку товаров

    if (!node.querySelector(".admin-panel_products-grid")) {
        deleteAdminsGrid(node);
        appendProductsGrid(node);

        const navbarButtons = node.querySelectorAll(".admin-panel_buttons a");
        navbarButtons[2].classList.remove("admin-panel_chosen-button");
        navbarButtons[1].classList.add("admin-panel_chosen-button");
    }
}
