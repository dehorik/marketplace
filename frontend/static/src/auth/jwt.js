function setToken(token) {
    localStorage.setItem("token", token);
}

function getToken() {
    return localStorage.getItem("token");
}

async function getVerifiedToken() {
    let token = getToken();

    if (verifyToken(token)) {
        return token;
    }
    else {
        await refresh();
        return getToken();
    }
}

function deleteToken() {
    localStorage.removeItem("token");
}

function decodeToken(token) {
    const base64url = token.split('.')[1];
    const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
        atob(base64)
            .split('')
            .map(c => `%${('00' + c.charCodeAt(0).toString(16)).slice(-2)}`)
            .join('')
    );
    return JSON.parse(jsonPayload);
}

function verifyToken(token) {
    return decodeToken(token).exp - Math.floor(Date.now() / 1000) > 30;
}
