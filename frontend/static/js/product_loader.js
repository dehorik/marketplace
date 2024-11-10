const grid = document.querySelector(".grid");


window.addEventListener("load", () => {
    State.deleteFromStorage();
    const state = new State();
    state.set("last_id", null);

    get_products(15);
    window.addEventListener("scroll", check_position);
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
    const product_uri = `/products/${product.product_id}`;

    const card = document.createElement("div");
    card.className = "product-card";

    const photo = document.createElement("div");
    const image_link = document.createElement("a");
    const image = document.createElement("img");
    photo.className = "product-photo";
    image_link.href = product_uri;
    image.src = product.photo_path;
    image.alt = "product-photo";
    image_link.append(image);
    photo.append(image_link);

    const price = document.createElement("div");
    price.className = "product-price";
    price.innerHTML = `${product.price} $`;

    const name = document.createElement("div");
    const text_link = document.createElement("a");
    name.className = "product-name";
    text_link.href = product_uri;
    text_link.innerHTML = product.name;
    name.append(text_link);

    const product_comments_summary = document.createElement("div");
    const average_rating = document.createElement("div");
    const star_image = document.createElement("img");
    const rating = document.createElement("span");
    const amount_comments = document.createElement("div");
    const comment_image = document.createElement("img");
    const amount = document.createElement("span");
    product_comments_summary.className = "product-comments-summary";
    average_rating.className = "average-rating";
    star_image.src = product.rating >= 4 ? "/static/img/active_star.png/" : "/static/img/inactive_star.png/";
    star_image.alt = "star";
    rating.innerHTML = product.rating !== Math.round(product.rating) ? product.rating : `${product.rating}.0`;
    amount_comments.className = "amount-comments";
    comment_image.src = "/static/img/comment.png";
    comment_image.alt = "comment";
    amount.innerHTML = product.amount_comments;
    average_rating.append(star_image);
    average_rating.append(rating);
    amount_comments.append(comment_image);
    amount_comments.append(amount);
    product_comments_summary.append(average_rating);
    product_comments_summary.append(amount_comments);

    card.append(photo);
    card.append(price);
    card.append(name);
    card.append(product_comments_summary);

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
