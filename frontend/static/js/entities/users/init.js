window.addEventListener("load", () => {
    getVerifiedToken()
        .then((token) => {
            axios({
                url: "/users/me",
                method: "get",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .then((response) => {
                    appendUserPage(response.data);
                })
                .catch(() => {
                    deleteToken();
                    window.location.href = "/auth/form";
                });
        })
        .catch(() => {
            deleteToken();
            window.location.href = "/auth/form";
        });
});
