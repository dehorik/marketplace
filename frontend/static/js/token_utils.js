function set_access_token(access_token) {
    localStorage.setItem("access_token", access_token);
}

function get_access_token() {
    return localStorage.getItem("access_token");
}

function delete_access_token() {
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

function check_access_token_exp(access_token) {
    const access_token_payload = parse_jwt(access_token);
    const exp_time = access_token_payload.exp * 1000;
    const time = Date.now();

    return exp_time - time <= 10000;
}

function refresh() {
    delete_access_token();

    axios.post("/auth/refresh")
        .then(function (response) {
            set_access_token(response.data.access_token);
        });
}
