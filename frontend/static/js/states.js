class CatalogStateData {
    constructor(last_id) {
        this.last_id = last_id;
    }
}


class SearchedProductStateData {
    constructor(name, last_id) {
        this.name = name;
        this.last_id = last_id;
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



