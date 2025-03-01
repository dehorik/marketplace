function deleteProduct(productId, node) {
    // апи запрос на удаление товара

    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/products/${productId}`,
                method: "delete",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then(() => {
                    if (node.parentNode.children.length === 1) {
                        appendAdminPanelProductsNotFoundMessage();
                    }

                    node.parentNode.removeChild(node);
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}