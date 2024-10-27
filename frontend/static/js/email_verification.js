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
            message_text.textContent = "Возникли неполадки во время подтверждения почты. Вероятно, письмо было просрочено. Повторите попытку привязки почты.";
        });
};
