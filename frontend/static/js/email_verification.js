window.onload = function () {
    const message = document.querySelector('.message');
    const token = new URLSearchParams(window.location.search).get('token');

    axios.patch('/users/email-verification', {
            token: token
        }
    )
        .then((response) => {
            message.innerHTML = "Почта была успешно подтверждена! <br>Вы можете покинуть эту страницу";
        })
        .catch((error) => {
            message.innerHTML = "Почта не подтверждена! <br>Повторите попытку привязки";
        });
};
