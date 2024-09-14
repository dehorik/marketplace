function set_token(access_token) {
    localStorage.setItem("access_token", access_token);
}

function get_token() {
    return localStorage.getItem("access_token");
}

function delete_token() {
    localStorage.removeItem("access_token");
}


function parse_jwt (token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

function check_token_exp(access_token) {
    const token_payload = parse_jwt(access_token);
    const exp_time = token_payload.exp * 1000;
    const time = Date.now();

    return exp_time - time <= 10000;
}

function refresh() {
    delete_token();

    axios.post("/auth/refresh")
        .then(function (response) {
            set_token(response.data.access_token);
        });
}


function verify_token() {
    const access_token = get_token();

    if (!access_token) {
        return;
    }

    if (check_token_exp(access_token)) {
        refresh();
    }
}