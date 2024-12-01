class CommentsLoadingState {
    constructor() {
        const data = JSON.parse(localStorage.getItem("state"));

        if (data && data.type === "loading_comments") {
            this.data = data;
        }
        else {
            this.data = {
                type: "loading_comments"
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
            type: "loading_comments"
        };
        localStorage.removeItem("state");
    }

    is_empty() {
        return Object.keys(this.data).length < 2;
    }
}


class CommentEditingState {
    constructor() {
        const data = JSON.parse(localStorage.getItem("state"));

        if (data && data.type === "editing_comment") {
            this.data = data;
        }
        else {
            this.data = {
                type: "editing_comment"
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
            type: "editing_comment"
        };
        localStorage.removeItem("state");
    }

    is_empty() {
        return Object.keys(this.data).length < 2;
    }
}
