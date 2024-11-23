function create_cart_item(product_id) {
    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJpYXQiOjE3MzIzNzkwNzAsImV4cCI6MTczMjM3OTk3MH0.tePw6q795l-n4jpDGzwxeE9XUYzVN0Cll1z0dwAc9wXUZXvQqScsupEJaYfJQWtm4glwJHEZoJA9yZj89YZumLB1VfIAquHrVsfWnmoVYK2QeF-z_V6jmERWVc0KQOG5H_4xerd_ogB9E-BkH4QC4dyxMoVby9X4RncCbJ_rxs-hjWqlNx1liXTJqCY_V-rrI4S1sHRRi5JRGlOevhxUg95vz-vYacuCH_GL4K4ED7WHUGCtN2r7TB8Dj7O_4FQqTI3GCsdvSRkBm_C17Atl7QC6u-WI7jAde85yZmgOPUoHsiZ3uKRwJh7DGyKLuIls_2Mg_Ruk7Fru8te_O-RD5g";

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
