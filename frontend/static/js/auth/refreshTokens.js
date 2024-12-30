async function refresh() {
    try {
        const response = await axios({
            url: "/auth/refresh",
            method: "post"
        });

        setToken(response.data.access_token);
    }
    catch (error) {
        deleteToken();

        throw new Error("not authenticated");
    }
}
