function deleteCartItem(cart_item_id) {
    getVerifiedToken()
        .then((token) => {
            axios({
                url: `/cart-items/${cart_item_id}`,
                method: "delete",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then(() => {

                })
                .catch(() => {

                });
        })
        .catch(() => {

        });
}
