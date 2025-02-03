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
