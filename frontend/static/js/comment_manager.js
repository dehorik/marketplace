function show_buttons(comment) {
    const comment_data = comment.querySelector(".comment-data-container");

    if (comment_data) {
        const height = comment.getBoundingClientRect().height;
        const buttons = comment.querySelector(".comment-buttons-container");

        comment_data.classList.add("no-display");
        buttons.classList.remove("no-display");
        buttons.style.height = `${height}px`;
    }
}

function hide_buttons(comment) {
    const comment_data = comment.querySelector(".comment-data-container");

    if (comment_data) {
        const buttons = comment.querySelector(".comment-buttons-container");

        buttons.classList.add("no-display");
        comment_data.classList.remove("no-display");
    }
}

function delete_comment(node, comment_id) {
    node.removeEventListener("click", delete_comment);
    node.removeEventListener("mouseenter", show_buttons);
    node.removeEventListener("mouseleave", hide_buttons);

    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJpYXQiOjE3MzI4OTMyMzEsImV4cCI6MTczMjk4MzIzMX0.EfMbZ6bQuDvhJuSiLP0UTBnQDk4OLVEmgLppLCI99Cd8Ibtz_FFSZ1hkWYzFgup2UuaLyCCxNh7FPDBlaFwJUCQdNj9VsP-IBzox_Ty6zjkznOYJ04_UyiSoKMIN_IOENw5ZohGhWv9Zyx0ByfEYfzlTCObIF6Jw5NDTsHkF3QxRb_CNe44ctelgshucyWCtSdfivTzxw9vB5rzKizqocKGuS5hfvZmgwKXDI-tqiBlVo4o4Edvo21nIYW1HOS_iI5RivWhzdrvBPDKB_tG5RrqfmYOKjnkPBS5TKd4O1qlOkVXF17gZlwxOcHvsyGdOz3yh5hnlvq9uwvgt0HVJHA";
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

            const amount_comments_node = document.getElementById("product-amount-comments");
            let amount_comments = Number(amount_comments_node.textContent) - 1;
            amount_comments_node.textContent = String(amount_comments);

            const product_rating_node = document.getElementById("product-rating");
            const star = document.querySelector(".product-rating img");
            let product_rating = 0;

            for (let node of document.querySelectorAll(".comment-stars")) {
                product_rating += Number(node.getAttribute("data-rating"));
            }

            product_rating = (product_rating / amount_comments).toFixed(1);
            product_rating_node.textContent = !isNaN(product_rating) ? String(product_rating) : '0.0';

            if (product_rating >= 4) {
                if (star.src !== "/static/img/active_star.png") {
                    star.src = "/static/img/active_star.png";
                }
            }
            else {
                if (star.src !== "/static/img/inactive_star.png") {
                    star.src = "/static/img/inactive_star.png";
                }
            }

            setTimeout(() => {
                node.style.backgroundColor = "rgba(236,237,240,0.94)";
                node.style.height = "0";
                node.style.margin = "0";
            }, 10);

            setTimeout(() => {
                grid.removeChild(node);

                if (grid.querySelectorAll(".comment").length === 0) {
                    get_message();
                }
            }, 1600);
        })
}
