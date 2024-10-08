function print_message(message) {
    const text = message.textContent;
    message.innerHTML = text.replace(/./g, '<span class="new">$&</span>');

    const span_elems= message.querySelectorAll('span.new');
    span_elems.forEach((span, i) => {
        setTimeout(() => {
            span.classList.add('div_opacity');
        }, 40 * i);
    });
}

function welcome_user(username, redirected_url="/") {
    const message = document.createElement('div');
    message.id = "welcome-message";
    message.innerHTML = `Добро пожаловать, ${username}!`;

    const body = document.createElement("body");
    body.append(message);
    document.body.replaceWith(body);

    print_message(message);

    setTimeout( () => {
            window.location.href = redirected_url;
        },
        1410
    );
}
