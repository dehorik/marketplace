function getAdmins(adminsGrid) {
    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/users",
                method: "get",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then((response) => {
                    for (let admin of response.data.users) {
                        appendAdmin(admin, adminsGrid);
                    }
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}

function appendAdmin(admin, adminsGrid) {
    adminsGrid.append(createAdminNode(admin));
}

function createAdminNode(admin) {
    const container = document.createElement("div");
    container.className = "admin-container";

    const node = document.createElement("div");
    node.className = "admin";

    const photoContainer = document.createElement("div");
    const photo = document.createElement("img");
    photoContainer.className = "admin-photo-container";
    if (admin.has_photo) {
        photo.src = `/images/users/${admin.user_id}.jpg?reload=${Date.now()}`;
    }
    else {
        photo.src = "/static/img/default-avatar.png"
    }
    photoContainer.appendChild(photo);

    const textDataContainer = document.createElement("div");
    const textData = document.createElement("div");
    const nameContainer = document.createElement("div");
    const roleContainer = document.createElement("div");
    const name = document.createElement("span");
    const role = document.createElement("span");
    textDataContainer.className =  "admin-text-data-container";
    textData.className = "admin-text-data";
    nameContainer.className = "admin-name-container";
    roleContainer.className = "admin-role-container";
    name.textContent = admin.username;
    role.textContent = admin.role_name;
    nameContainer.appendChild(name);
    roleContainer.appendChild(role);
    textData.appendChild(nameContainer);
    textData.appendChild(roleContainer);
    textDataContainer.appendChild(textData);

    const buttonsContainer = document.createElement("div");
    const buttons = document.createElement("div");
    const editingButton = document.createElement("a");
    const deleteButton = document.createElement("a");
    const editingButtonText = document.createElement("span");
    const deleteButtonText = document.createElement("span");
    buttonsContainer.className = "admin-buttons-container";
    buttons.className = "admin-buttons";
    editingButtonText.textContent = "Изменить роль";
    deleteButtonText.textContent = "Удалить администратора";
    editingButton.appendChild(editingButtonText);
    deleteButton.appendChild(deleteButtonText);
    buttons.appendChild(editingButton);
    buttons.appendChild(deleteButton);
    buttonsContainer.appendChild(buttons);

    node.appendChild(photoContainer);
    node.appendChild(textDataContainer);
    node.appendChild(buttonsContainer);
    container.appendChild(node);

    return container;
}
