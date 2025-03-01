async function refresh() {
    // запрос на обновление пары jwt токенов

    try {
        const response = await axios({
            url: "/auth/refresh",
            method: "post"
        });

        setToken(response.data.access_token);
    }
    catch (error) {
        deleteToken();
        throw error;
    }
}
