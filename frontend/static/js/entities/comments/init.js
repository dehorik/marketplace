const grid = document.querySelector(".comments-grid");


window.addEventListener("load", () => {
    const state = new State();
    state.clear();
    state.set("product_id", window.location.pathname.split("/").slice(-1)[0]);
    state.set("last_id", null);

    setTimeout(() => {
        const observer = new MutationObserver(() => {
            if (grid.querySelectorAll(".comment").length <= 10) {
                window.removeEventListener("scroll", checkPosition);
                setTimeout(() => {
                    window.addEventListener("scroll", checkPosition);
                }, 250);

                getComments();
            }
        });
        observer.observe(grid, {
            childList: true,
            subtree: true
        });

        window.addEventListener("scroll", checkPosition);

        const comment_creation_button = document.querySelector(".comment-creation-link");

        if (comment_creation_button) {
            comment_creation_button.addEventListener("click", appendCommentForm);
        }
    }, 500);

    getComments();
});
