function create_cart_item(product_id) {
    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoxLCJpYXQiOjE3MzI0NTQwMjUsImV4cCI6MTczMjU0NDAyNX0.uDFmrpptQlVsvXc9C3q7-QZFx1D4yxOISGImKsNsHORp3CgZh8QhrqjuKNhwIAfwAyDeL98XvBn0hJZcfTK2T0IADCAbm0BDXUlbTqZ6Zs69xBOM-nS37t7M8vSP0BTAd8FQ93JG-qMq1jLfB6K_I1LCHbVjN7mAK4XMUgdSwBM91cxtBI42X1pggLJJ1GjGaHNAoVc5qBzC9hu0A_E3x5ioCUYlZK8kasXwtXKazQIbLm7xhuq-pQKMqKe1yIU5rMJA15F3W3Zu1L5P95dZQdSKafmlibDFZejET46rPcjOSNbXpOsXRPRoKG431wAhE8ukQ7vnJLbOY4zb_VdA6w";

    axios({
        url: "/orders/cart",
        method: "post",
        headers: {
            "Authorization": `Bearer ${jwt}`
        },
        data: {
            "product_id": product_id
        }
    })
        .then(() => {
            const cart_items_link = document.createElement("div");
            const link = document.createElement("a");
            const text = document.createElement("span");
            cart_items_link.className = "cart-items-link";
            link.href = "#";
            text.textContent = "Уже в корзине";
            link.append(text);
            cart_items_link.append(link);

            document.querySelector(".cart-item-creation-button").replaceWith(cart_items_link);
        })
}
