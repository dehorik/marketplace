function show_buttons(comment) {
    const comment_data = comment.querySelector(".comment-data-container");
    const buttons = comment.querySelector(".comment-buttons-container");
    const height = comment_data.getBoundingClientRect().height;

    comment_data.classList.add("no-display");
    buttons.classList.remove("no-display");
    buttons.style.height = `${height}px`;
}

function hide_buttons(comment) {
    const comment_data = comment.querySelector(".comment-data-container");
    const buttons = comment.querySelector(".comment-buttons-container");

    if (!comment_data) {
        return;
    }

    buttons.classList.add("no-display");
    comment_data.classList.remove("no-display");
}

function delete_comment(node, comment_id) {
    const jwt = "сюда жвт совать пока не приделал аутентификацию";

    axios.delete(`/comments/${comment_id}`, {
        headers: {
            "Authorization": `Bearer ${jwt}`
        }
    })
        .then(() => {
            node.removeChild(node.firstChild);
            node.style.height = node.offsetHeight + "px";
            node.style.transition = "height 1.6s ease, margin 1.6s ease";

            while (node.firstChild.firstChild) {
                node.firstChild.removeChild(node.firstChild.firstChild);
            }

            setTimeout(() => {
                node.style.backgroundColor = "rgba(236,237,240,0.94)";
                node.style.height = "0";
                node.style.margin = "0";
                node.style.overflow = "hidden";
            }, 10);

            setTimeout(() => {
                grid.removeChild(node);
            }, 1610);






        });
}