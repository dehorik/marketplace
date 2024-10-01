window.addEventListener('load', () => {
    update_catalog(9);
    window.addEventListener('scroll', check_position);

    localStorage.removeItem("searching");
});


function update_catalog(amount, last_product_id) {
    // amount: кол-во товаров, которые будут вытащенны
    // last_product_id: product_id последнего товара на текущей странице.
    // я добавил к тегу div, содержащему карточку товара, атрибут data-product-id;
    // он необходим для корректной работы скрипта

    let url = "/products/latest";
    let params = {
        amount: amount,
        last_product_id: last_product_id
    };

    if (localStorage.getItem("searching")) {
        url = "/products/search";
        params = {
            product_name: localStorage.getItem("searching"),
            amount: 9,
            last_product_id: last_product_id
        }
    }

    axios.get(url, {params})
        .then(function (response) {
            let products = response.data.products;

            for (let i in products) {
                const product = products[i];
                const item = create_item(product);
                place_item(item);
            }
        });
}

function create_item(product) {
    // создаём дом узел и возвращаем его

    const item = document.createElement('div');
    item.className = "merchants-item";
    item.setAttribute("data-product-id", product.product_id);

    const product_photo = document.createElement('div');
    product_photo.className = "merchants-item-image";
    const img = document.createElement('img');
    img.src = product.product_photo_path;
    product_photo.append(img);

    const product_name = document.createElement('div');
    product_name.className = "merchants-item-text";
    const link = document.createElement('a');
    link.href = `/products/${product.product_id}`;
    link.innerHTML = product.product_name;
    product_name.append(link);

    // не ебу, зачем эти блоки, просто они были в html разметке
    // вопросов не вызывает только divprice
    const divextra = document.createElement('div');
    divextra.className = "merchants-item-extra";
    const divinfo = document.createElement('div');
    divinfo.className = "merchants-item-info";
    const divprice = document.createElement('div');
    divprice.setAttribute('data-base-price', '7'); //чё это бля? ты думал, что сервер может не вернуть цену?
    divprice.className = "merchants-item-price";
    divprice.innerHTML = `${product.product_price} $`;
    divextra.append(divinfo);
    divinfo.append(divprice);

    item.append(product_photo);
    item.append(product_name);
    item.append(divextra);

    return item;
}

function place_item(item) {
    // размещаем новый дом узел

    const grid = document.body.querySelector(".merchants-items");
    grid.append(item);
}

function check_position() {
    // ну а эта шняга нужна, чтобы понять, когда просить добавки у сервера

    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    // подгружаем товары заранее
    if (documentHeight - (windowHeight + scrollPosition) <= 170) {
        const product = document.body.querySelector(".merchants-item:last-of-type");
        const last_product_id = Number(product.getAttribute("data-product-id"));
        update_catalog(9, last_product_id);

        // после отправки запроса на обновление каталога,
        // должно пройти минимум 300мс, чтобы отправить новый
        window.removeEventListener('scroll', check_position);
        setTimeout(
            () => {
                window.addEventListener('scroll', check_position)
            },
            300
        );
    }
}
