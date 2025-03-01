function logout() {
    // запрос на выход из аккаунта

    deleteToken();
    window.location.href = "/";

    axios({
        url: "/auth/logout",
        method: "post"
    });
}
