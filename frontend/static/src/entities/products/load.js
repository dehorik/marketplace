function getProducts() {
    let state = new State();

    if (!state.isEmpty()) {
        let configuration = {
            url: "/products/latest",
            method: "get",
            params: {
                amount: 30,
                last_id: state.get("last_id")
            }
        };

        if (state.get("name")) {
            configuration.url = "/products/search";
            configuration.params.name = state.get("name");
        }

        axios(configuration)
            .then((response) => {
                let products = response.data.products;

                if (products.length === 0) {
                    state.clear();

                    if (!productsGrid.firstChild) {
                        appendProductsNotFoundMessage();
                    }
                }
                else {
                    state.set("last_id", products.slice(-1)[0].product_id);

                    for (let product of products) {
                        appendProduct(product);
                    }
                }
            });
    }
}

function appendProduct(product) {
    productsGrid.append(createProductNode(product));
}

function createProductNode(product) {
    const productUrl = `/products/${product.product_id}`;

    const container = document.createElement("div");
    container.className = "product-catalog-card";

    const photoContainer = document.createElement("div");
    const photoLink = document.createElement("a");
    const photo = document.createElement("img");
    photoContainer.className = "product-catalog-card-photo";
    photoLink.href = productUrl;
    photo.src = `/images/products/${product.product_id}.jpg?reload=${Date.now()}`;
    photo.alt = "photo";
    photoLink.append(photo);
    photoContainer.append(photoLink);

    const price = document.createElement("div");
    price.className = "product-catalog-card-price";
    price.textContent = `${product.price} $`;

    const nameContainer = document.createElement("div");
    const name = document.createElement("a");
    nameContainer.className = "product-catalog-card-name";
    name.href = productUrl;
    name.textContent = product.name;
    nameContainer.append(name);

    const commentsSummary = document.createElement("div");
    const averageRating = document.createElement("div");
    const starImg = document.createElement("img");
    const rating = document.createElement("span");
    const amountComments = document.createElement("div");
    const commentImg = document.createElement("img");
    const amount = document.createElement("span");
    commentsSummary.className = "product-catalog-card-score";
    averageRating.className = "product-catalog-card-rating";
    starImg.src = product.rating >= 4 ? "/static/img/active_star.png/" : "/static/img/inactive_star.png/";
    starImg.alt = "star";
    rating.textContent = product.rating !== Math.round(product.rating) ? product.rating : `${product.rating}.0`;
    amountComments.className = "product-catalog-card-amount-comments";
    commentImg.src = "/static/img/comment.png";
    commentImg.alt = "comment";
    amount.textContent = product.amount_comments;
    averageRating.append(starImg);
    averageRating.append(rating);
    amountComments.append(commentImg);
    amountComments.append(amount);
    commentsSummary.append(averageRating);
    commentsSummary.append(amountComments);

    container.append(photoContainer);
    container.append(price);
    container.append(nameContainer);
    container.append(commentsSummary);

    return container;
}

function appendProductsNotFoundMessage() {
    const message = document.createElement("div");
    message.className = "index-message";
    message.textContent = "Ничего не найдено!";
    productsGrid.append(message);
}

function checkPosition() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 300) {
        window.removeEventListener("scroll", checkPosition);
        setTimeout(() => {
            window.addEventListener("scroll", checkPosition);
        }, 200);

        getProducts();
    }
}
