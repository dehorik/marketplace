class State {
    // класс для создания объектов состояния, хранящих временные данные
    // для параметризации get запросов

    constructor() {
        // создаем объект состояния на основе данных из localStorage

        let data = JSON.parse(localStorage.getItem("state"));

        if (data) {
            this.data = data;
        }
        else {
            this.data = {};
        }
    }

    get(key) {
        // получение данных о состоянии по ключу

        return this.data[key];
    }

    set(key, value) {
        // запись в состояние данных по ключу

        this.data[key] = value;
        localStorage.setItem("state", JSON.stringify(this.data));
    }

    delete(key) {
        // удаление данных из состояния по ключу

        delete this.data[key];
        localStorage.setItem("state", JSON.stringify(this.data));
    }

    hasProperty(key) {
        // проверка наличия данных в состоянии по ключу

        return Object.prototype.hasOwnProperty.call(this.data, key);
    }
}
