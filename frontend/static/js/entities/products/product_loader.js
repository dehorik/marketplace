const grid = document.querySelector(".products-grid");


window.addEventListener("load", () => {
    const form = document.getElementById("search-form");
    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const input = document.getElementById("search-input");

        if (input.value.length === 0) {
            location.reload();
        }
        else {
            while (grid.firstChild) {
                grid.removeChild(grid.firstChild);
            }

            const state = new ProductSearchingState();
            state.clear();
            state.set("name", input.value);
            state.set("last_id", null);

            get_products();
        }
    });

    const state = new ProductsLoadingState();
    state.clear();
    state.set("last_id", null);

    get_products();
    window.addEventListener("scroll", check_position);
});

function get_products() {
    let state = new ProductsLoadingState();

    if (state.is_empty()) {
        state = new ProductSearchingState();
    }

    let configuration = {
        url: "/products/latest",
        method: "get",
        params: {
            amount: 15,
            last_id: state.get("last_id")
        }
    };

    if (state.get("type") === "searching_product") {
        configuration.url = "/products/search";
        configuration.params.name = state.get("name");
        configuration.params.last_id = state.get("last_id");
    }

    axios(configuration)
        .then((response) => {
            let products = response.data.products;

            if (products.length === 0) {
                state.clear();

                if (!grid.querySelector(".product-catalog-card")) {
                    const message_area = document.createElement("div");
                    message_area.className = "index-message";
                    message_area.textContent = "Ничего не найдено!";
                    grid.append(message_area);
                }

                return;
            }

            state.set("last_id", products.slice(-1)[0].product_id);

            for (let i in products) {
                append(products[i]);
            }
        });
}

function append(product) {
    product = create_node(product);
    grid.append(product);
}

function create_node(product) {
    const product_uri = `/products/${product.product_id}`;

    const card = document.createElement("div");
    card.className = "product-catalog-card";

    const photo = document.createElement("div");
    const image_link = document.createElement("a");
    const image = document.createElement("img");
    photo.className = "product-catalog-card-photo";
    image_link.href = product_uri;
    image.src = `/${product.photo_path}`;
    image.alt = "photo";
    image_link.append(image);
    photo.append(image_link);

    const price = document.createElement("div");
    price.className = "product-catalog-card-price";
    price.textContent = `${product.price} $`;

    const name = document.createElement("div");
    const text_link = document.createElement("a");
    name.className = "product-catalog-card-name";
    text_link.href = product_uri;
    text_link.textContent = product.name;
    name.append(text_link);

    const product_comments_summary = document.createElement("div");
    const average_rating = document.createElement("div");
    const star_image = document.createElement("img");
    const rating = document.createElement("span");
    const amount_comments = document.createElement("div");
    const comment_image = document.createElement("img");
    const amount = document.createElement("span");
    product_comments_summary.className = "product-catalog-card-score";
    average_rating.className = "product-catalog-card-rating";
    star_image.src = product.rating >= 4 ? "/static/img/active_star.png/" : "/static/img/inactive_star.png/";
    star_image.alt = "star";
    rating.textContent = product.rating !== Math.round(product.rating) ? product.rating : `${product.rating}.0`;
    amount_comments.className = "product-catalog-card-amount-comments";
    comment_image.src = "/static/img/comment.png";
    comment_image.alt = "comment";
    amount.textContent = product.amount_comments;
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
        get_products();
        window.removeEventListener("scroll", check_position);

        setTimeout(() => {
            window.addEventListener("scroll", check_position);
        }, 250);
    }
}
