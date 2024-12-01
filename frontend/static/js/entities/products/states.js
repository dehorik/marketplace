class ProductsLoadingState {
    constructor() {
        const data = JSON.parse(localStorage.getItem("state"));

        if (data && data.type === "loading_products") {
            this.data = data;
        }
        else {
            this.data = {
                type: "loading_products"
            };
        }
    }

    get(key) {
        return this.data[key];
    }

    set(key, value) {
        this.data[key] = value;
        localStorage.setItem("state", JSON.stringify(this.data));
    }

    clear() {
        this.data = {
            type: "loading_products"
        };
        localStorage.removeItem("state");
    }

    is_empty() {
        return Object.keys(this.data).length < 2;
    }
}


class ProductSearchingState {
    constructor() {
        const data = JSON.parse(localStorage.getItem("state"));

        if (data && data.type === "searching_product") {
            this.data = data;
        }
        else {
            this.data = {
                type: "loading_products"
            };
        }
    }

    get(key) {
        return this.data[key];
    }

    set(key, value) {
        this.data[key] = value;
        localStorage.setItem("state", JSON.stringify(this.data));
    }

    clear() {
        this.data = {
            type: "loading_products"
        };
        localStorage.removeItem("state");
    }

    is_empty() {
        return Object.keys(this.data).length < 2;
    }
}
