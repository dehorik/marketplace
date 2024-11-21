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

    buttons.classList.add("no-display");
    comment_data.classList.remove("no-display");
}