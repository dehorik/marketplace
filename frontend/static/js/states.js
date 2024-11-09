class State {
    constructor() {
        const state_data = State.getStateData();
        this.data = state_data ? state_data : {};
    }

    static getStateData() {
        return JSON.parse(localStorage.getItem("state"));
    }

    static deleteFromStorage() {
        localStorage.removeItem("state");
    }

    saveToStorage() {
        localStorage.setItem("state", JSON.stringify(this.data));
    }

    get(key) {
        return this.data[key];
    }

    set(key, value) {
        this.data[key] = value;
        this.saveToStorage();
    }
}
