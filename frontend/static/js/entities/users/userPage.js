function appendUserPage(user) {
    const container = document.querySelector(".user-page_container");

    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    container.appendChild(getUserPage(user));
}

function getUserPage(user) {
    const container = document.createElement("div");
    container.className = "user-page";

    const data = document.createElement("div");
    data.className = "user-page_data";

    const photo_container = document.createElement("div");
    const photo = document.createElement("img");
    photo_container.className = "user-page_user-photo";
    photo.src = user.photo_path ? `/${user.photo_path}?reload=${Date.now()}` : "/static/img/default-avatar.png";
    photo.alt = user;
    photo_container.appendChild(photo);

    const text_data_container = document.createElement("div");
    text_data_container.className = "user-page_text-data-container";

    const username_container = document.createElement("div");
    const username = document.createElement("span");
    username_container.className = 'user-page_username';
    username.textContent = user.username;
    username_container.appendChild(username);

    const email_container = document.createElement("div");
    const email = document.createElement("span");
    email_container.className = 'user-page_email';
    email.textContent = user.email ? user.email : "Почта ещё не привязана";
    email_container.appendChild(email);

    const registration_date_container = document.createElement("div");
    const registration_date = document.createElement("span");
    registration_date_container.className = 'user-page_registration-date';
    registration_date.textContent = `Дата регистрации: ${user.registration_date}`;
    registration_date_container.appendChild(registration_date);

    text_data_container.append(username_container, email_container, registration_date_container);
    data.append(photo_container, text_data_container);

    const data_management_buttons_container = document.createElement("div");
    data_management_buttons_container.className = "user-page_data-management";

    const data_editing_btn_container = document.createElement("div");
    const data_editing_btn = document.createElement("a");
    const data_editing_btn_text = document.createElement("span");
    data_editing_btn_container.className = "user-page_data-editing-btn";
    data_editing_btn_text.textContent = "Изменить данные";
    data_editing_btn.appendChild(data_editing_btn_text);
    data_editing_btn_container.appendChild(data_editing_btn);

    const logout_btn_container = document.createElement("div");
    const logout_btn = document.createElement("a");
    const logout_btn_text = document.createElement("span");
    logout_btn_container.className = "user-page_logout-btn";
    logout_btn_text.textContent = "Выйти из аккаунта";
    logout_btn.appendChild(logout_btn_text);
    logout_btn_container.appendChild(logout_btn);

    const deletion_btn_container = document.createElement("div");
    const deletion_btn = document.createElement("a");
    const deletion_btn_text = document.createElement("span");
    deletion_btn_container.className = "user-page_account-deletion-btn";
    deletion_btn_text.textContent = "Удалить аккаунт";
    deletion_btn.appendChild(deletion_btn_text);
    deletion_btn_container.appendChild(deletion_btn);

    data_management_buttons_container.appendChild(data_editing_btn_container);
    data_management_buttons_container.appendChild(logout_btn_container);
    data_management_buttons_container.appendChild(deletion_btn_container);

    const navbar = document.createElement("div");
    navbar.className = "user-page_navbar";

    const catalog_btn_container = document.createElement("div");
    const catalog_btn = document.createElement("a");
    const catalog_btn_text = document.createElement("span");
    catalog_btn.href = "/";
    catalog_btn_text.textContent = "Каталог";
    catalog_btn.appendChild(catalog_btn_text);
    catalog_btn_container.appendChild(catalog_btn);

    const cart_btn_container = document.createElement("div");
    const cart_btn = document.createElement("a");
    const cart_btn_text = document.createElement("span");
    cart_btn.href = "/";
    cart_btn_text.textContent = "Корзина";
    cart_btn.appendChild(cart_btn_text);
    cart_btn_container.appendChild(cart_btn);

    const orders_btn_container = document.createElement("div");
    const orders_btn = document.createElement("a");
    const orders_btn_text = document.createElement("span");
    orders_btn.href = "/";
    orders_btn_text.textContent = "Мои заказы";
    orders_btn.appendChild(orders_btn_text);
    orders_btn_container.appendChild(orders_btn);

    navbar.appendChild(catalog_btn_container);
    navbar.appendChild(cart_btn_container);
    navbar.appendChild(orders_btn_container);

    if (user.role_id >= 2) {
        const admin_btn_container = document.createElement("div");
        const admin_btn = document.createElement("a");
        const admin_btn_text = document.createElement("span");
        admin_btn_text.textContent = "Панель управления";
        admin_btn.appendChild(admin_btn_text);
        admin_btn_container.appendChild(admin_btn);

        navbar.appendChild(admin_btn_container);
    }

    container.appendChild(data);
    container.appendChild(data_management_buttons_container);
    container.appendChild(navbar);

    data_editing_btn.addEventListener("click", () => {
        appendUserForm(user);
    });

    logout_btn.addEventListener("click", logout);

    return container;
}
