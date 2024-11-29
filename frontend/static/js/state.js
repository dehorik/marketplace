class State {
    constructor() {
        const state_data = JSON.parse(localStorage.getItem("state"));
        this.data = state_data ? state_data : {};
    }

    clearState() {
        this.data = {};
        localStorage.removeItem("state");
    }

    get(key) {
        return JSON.parse(localStorage.getItem("state"))[key];
    }

    set(key, value) {
        this.data[key] = value;
        localStorage.setItem("state", JSON.stringify(this.data));
    }
}
