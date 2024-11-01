const product_grid = document.querySelector(".merchants-items");
const message_area = document.querySelector(".message-area");


window.addEventListener('load', () => {
    State.deleteFromStorage();
    const state_data = new CatalogStateData(null);
    const state = new State(state_data);
    state.saveToStorage();

    update_catalog();
    window.addEventListener('scroll', check_position);
});


function update_catalog(amount=9) {
    const state = get_state_obj();

    let url = "/products/latest";
    let params = {
        amount: amount,
        last_id: state.data.last_id
    };

    if (state.data.name) {
        url = "/products/search";
        params = {
            name: state.data.name,
            amount: amount,
            last_id: state.data.last_id
        }
    }

    axios.get(url, {params})
        .then(function (response) {
            let products = response.data.products;

            if (products.length === 0 && product_grid.innerHTML === "") {
                message_area.innerHTML = "Ничего не найдено!";
            }
            else if (products.length !== 0){
                state.data.last_id = products.slice(-1)[0].product_id;
                state.saveToStorage();

                for (let i in products) {
                    place_item(create_item(products[i]));
                }
            }
        });
}

function create_item(product) {
    const product_card = document.createElement('div');
    product_card.className = "merchants-item";

    const product_photo = document.createElement('div');
    product_photo.className = "merchants-item-image";
    const img = document.createElement('img');
    img.src = product.photo_path;
    product_photo.append(img);

    const product_name = document.createElement('div');
    product_name.className = "merchants-item-text";
    const link = document.createElement('a');
    link.href = `/products/${product.product_id}`;
    link.innerHTML = product.name;
    product_name.append(link);

    const wrapper1 = document.createElement('div');
    wrapper1.className = "merchants-item-extra";
    const wrapper2 = document.createElement('div');
    wrapper2.className = "merchants-item-info";
    const product_price = document.createElement('div');
    product_price.setAttribute('data-base-price', '7');
    product_price.className = "merchants-item-price";
    product_price.innerHTML = `${product.price} $`;
    wrapper1.append(wrapper2);
    wrapper2.append(product_price);

    product_card.append(product_photo);
    product_card.append(product_name);
    product_card.append(wrapper1);

    return product_card;
}

function place_item(item) {
    product_grid.append(item);
}

function check_position() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 170) {
        update_catalog();

        // после отправки запроса на обновление каталога,
        // должно пройти минимум 200мс, чтобы отправить новый
        window.removeEventListener('scroll', check_position);

        setTimeout(
            () => {
                window.addEventListener('scroll', check_position)
            },
            200
        );
    }
}
