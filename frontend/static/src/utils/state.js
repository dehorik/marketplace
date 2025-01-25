class State {
    constructor() {
        let data = JSON.parse(localStorage.getItem("state"));

        if (data) {
            this.data = data;
        }
        else {
            this.data = {};
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
        this.data = {};
        localStorage.removeItem("state");
    }

    isEmpty() {
        return Object.keys(this.data).length === 0;
    }
}
