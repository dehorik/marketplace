function print_message(message_elem) {
    const text = message_elem.textContent;
    message_elem.innerHTML = text.replace(/./g, '<span class="new">$&</span>');

    const span_elems= message_elem.querySelectorAll('span.new');
    span_elems.forEach((span, i) => {
        setTimeout(() => {
            span.classList.add('div_opacity');
        }, 40 * i);
    });
}

function get_message(user, redirected_url) {
    const body = document.createElement("body");
    const message_elem = document.createElement('div');
    message_elem.id = "successful_auth_message";
    message_elem.innerHTML = `Добро пожаловать, ${user.user_name}!`;

    body.append(message_elem);
    document.body.replaceWith(body);

    print_message(message_elem);
    setTimeout( () => {
            window.location.href = redirected_url;
        },
        1410
    );
}
