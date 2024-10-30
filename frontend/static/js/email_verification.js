window.onload = function () {
    const token = new URLSearchParams(window.location.search).get('token');
    const message_title = document.getElementById('message-title');
    const message_text = document.getElementById('message-text');

    axios.patch('/users/email-verification', {
            token: token
        }
    )
        .then((response) => {
            message_title.textContent = "Почта подтверждена!";
            message_text.textContent = "Спасибо за подтверждение вашей почты. Теперь вы можете пользоваться всеми функциями маркетплейса.";
        })
        .catch((error) => {
            message_title.textContent = "Почта не подтверждена!";

            if (error.response.status === 404) {
                message_text.textContent = "Похоже, ваша учётная запись была удалена из нашего сервиса =(";
            }
            else {
                message_text.textContent = "Возникли неполадки во время подтверждения почты. Вероятно, письмо было просрочено. Повторите попытку привязки почты.";
            }
        });
};
