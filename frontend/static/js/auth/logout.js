function logout() {
    axios({
        url: "auth/logout",
        method: "post"
    })
        .then(() => {
            deleteToken();
        })
        .catch(() => {
            deleteToken();

            throw new Error("not authenticated");
        });
}