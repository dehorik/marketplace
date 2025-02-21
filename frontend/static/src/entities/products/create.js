function createProduct(name, price, description, photo, form) {
    getVerifiedToken()
        .then((token) => {
            const data = new FormData();

            data.append("name", name);
            data.append("price", price);
            data.append("description", description);
            data.append("photo", photo);

            axios({
                url: "/products",
                method: "post",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: data
            })
                .then((response) => {
                    const productsGrid = document.querySelector(".admin-panel_products-grid");
                    const productNode = createAdminProductNode(response.data);

                    productsGrid.prepend(productNode);

                    deleteProductForm(form.parentNode.parentNode);
                })
                .catch(() => {
                    const errorText = document.querySelector(".product-form-error-container span");
                    errorText.textContent = "Товар не был создан";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}
