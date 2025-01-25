function logout() {
    deleteToken();
    window.location.href = "/";

    axios({
        url: "/auth/logout",
        method: "post"
    });
}
