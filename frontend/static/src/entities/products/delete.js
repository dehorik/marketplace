function deleteProduct(productId, node) {
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
                        appendAdminProductsNotFoundMessage();
                    }

                    node.parentNode.removeChild(node);
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form?redirect_url=/users/me/home";
        });
}