function setToken(token) {
    // сохранение access токена в localStorage

    localStorage.setItem("token", token);
}

function getToken() {
    // получение access токена из localStorage

    return localStorage.getItem("token");
}

async function getVerifiedToken() {
    // делает запрос на обновление access токена, если срок жизни истекает, иначе возвращает старый

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
    // удаляет access токен из localStorage

    localStorage.removeItem("token");
}

function decodeToken(token) {
    // декодирует access токен

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
    // проверяет, не истёк ли срок жизни access токена

    return decodeToken(token).exp - Math.floor(Date.now() / 1000) > 30;
}
