window.addEventListener("load", () => {
    const token = new URLSearchParams(window.location.search).get('token');
    const status = document.querySelector(".email-verification_status span");

    if (!token) {
        status.textContent = "Невалидный адрес!";
    }
    else {
        axios({
            url: "/users/email-verification",
            method: "patch",
            data: {
                token: token
            }
        })
            .then((response) => {
                status.innerHTML = `Почта <b>${response.data.email}</b> была успешно привязана к аккаунту <b>${response.data.username}</b>. Вы можете покинуть эту страницу и продолжить покупки.`;
            })
            .catch(() => {
                status.textContent = "Ваша почта не была привязана к аккаунту. Вероятно, срок действия письма истёк.";
                status.style.textAlign = "center";
            });
    }
});
