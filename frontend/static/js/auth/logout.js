function logout() {
    axios({
        url: "/auth/logout",
        method: "post"
    })
        .then(() => {
            deleteToken();
            window.location.href = "/";
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/";

            throw new Error("not authenticated");
        });
}
