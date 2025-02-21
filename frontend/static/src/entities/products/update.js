function updateProduct(productId, name, price, description, photo, form, productNode) {
    getVerifiedToken()
        .then((token) => {
            const data = new FormData();

            if (name) data.append("name", name);
            if (price) data.append("price", price);
            if (description) data.append("description", description);
            if (photo) data.append("photo", photo);

            axios({
                url: `/products/${productId}`,
                method: "patch",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                data: data
            })
                .then((response) => {
                    const productsGrid = document.querySelector(".admin-panel_products-grid");
                    const updatedProductNode = createAdminProductNode(response.data);

                    productsGrid.replaceChild(updatedProductNode, productNode);

                    deleteProductForm(form.parentNode.parentNode);
                })
                .catch(() => {
                    const errorText = document.querySelector(".product-form-error-container span");
                    errorText.textContent = "Товар не был изменён";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}