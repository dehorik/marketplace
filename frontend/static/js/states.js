class CatalogStateData {
    constructor(last_product_id) {
        this.last_product_id = last_product_id;
    }
}


class SearchedProductStateData {
    constructor(product_name, last_product_id) {
        this.product_name = product_name;
        this.last_product_id = last_product_id;
    }
}


class State {
    constructor(data) {
        this.data = data;
    }

    static getStateData() {
        return JSON.parse(localStorage.getItem("state"));
    }

    saveToStorage() {
        localStorage.setItem("state", JSON.stringify(this.data));
    }

     static deleteFromStorage() {
        localStorage.removeItem("state");
    }
}


function get_state_obj() {
    return new State(State.getStateData());
}



