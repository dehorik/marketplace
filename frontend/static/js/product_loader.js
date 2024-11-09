const grid = document.querySelector(".grid");


window.addEventListener("load", () => {
    State.deleteFromStorage();
    const state = new State();
    state.set("last_id", null)

    window.addEventListener("scroll", check_position);
    get_products(15);
});


function get_products(amount = 15) {
    const state = new State();

    if (Object.keys(state.data).length === 0) {
        return;
    }

    let url = "/products/latest";
    let params = {
        amount: amount,
        last_id: state.get("last_id")
    };

    if (state.get("name")) {
        url = "/products/search";
        params["name"] = state.get("name");
    }

    axios.get(url, {params})
        .then((response) => {
            let products = response.data.products;

            if (products.length === 0) {
                State.deleteFromStorage();

                if (!grid.querySelector(".product-card")) {
                    get_message();
                }

                return;
            }

            state.set("last_id", products.slice(-1)[0].product_id);

            for (let i in products) {
                append(products[i]);
            }
        });
}

function get_message() {
    const message_area = document.createElement("div");
    message_area.className = "message-area";
    message_area.innerHTML = "Ничего не найдено!";
    grid.append(message_area);
}

function append(product) {
    product = create_node(product);
    grid.append(product);
}

function create_node(product) {
    const card = document.createElement("div");
    card.className = "product-card";

    const photo = document.createElement("div");
    photo.className = "product-photo";
    const link1 = document.createElement("a");
    link1.href = `/products/${product.product_id}`;
    const image = document.createElement("img");
    image.src = product.photo_path;
    image.alt = "product-photo";
    link1.append(image);
    photo.append(link1);

    const price = document.createElement("div");
    price.className = "product-price";
    price.innerHTML = `${product.price} $`;

    const name = document.createElement("div");
    name.className = "product-name";
    const link2 = document.createElement("a");
    link2.href = `/products/${product.product_id}`;
    link2.innerHTML = product.name;
    name.append(link2);

    const rating_data = document.createElement("rating");
    rating_data.className = "rating-data";
    const product_rating = document.createElement("div");
    product_rating.className = "product-rating";
    const star = document.createElement("img");
    star.src = product.rating >= 4 ? "/static/img/active_star.png/" : "/static/img/inactive_star.png/";
    star.alt = "star";
    const rating = document.createElement("span");
    rating.innerHTML = product.rating !== Math.round(product.rating) ? product.rating : String(product.rating) + ".0";
    product_rating.append(star);
    product_rating.append(rating);
    const amount_comments = document.createElement("div");
    amount_comments.className = "amount-comments";
    const comment = document.createElement("img");
    comment.src = "/static/img/comment.png";
    comment.alt = "comment";
    const amount = document.createElement("span");
    amount.innerHTML = product.amount_comments;
    amount_comments.append(comment);
    amount_comments.append(amount);
    rating_data.append(product_rating);
    rating_data.append(amount_comments);

    card.append(photo);
    card.append(price);
    card.append(name);
    card.append(rating_data);

    return card;
}

function check_position() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 170) {
        get_products(15);
    }
}
