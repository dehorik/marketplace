function show_buttons(comment) {
    const comment_data = comment.querySelector(".comment-data-container");
    const buttons = comment.querySelector(".comment-buttons-container");

    if (!comment_data) {
        return;
    }

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
    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJpYXQiOjE3MzIzODIwODAsImV4cCI6MTczMjM4Mjk4MH0.hInYtSJYiujxej_FBpbWzFDncbqtzMHlGcY9wvs1VNz38m48n7NfDcyzm6426xne9Ly2DSL0Zj8RTcuIscTjgu73gNUYTKjGjjfjLgQ5lvoFIKLh2rPHAtqRqfI1Dq4GmhwrPq8ABoVpkH-gi5X77pK5ObpZLNkilsEALceRaAOlpWALnedCXXa7mRbdrsmaph9fgOD17rSk5RbDaGXUvZlGHulteTtJ8o8xv8pdX78FV8TCphQY8EL1X6WPHMRIvHXMZ24GqiMk82qooZtPqheePvsXQdlsUTCZZ5QO76oi4s38ibONN4KeSDibLhmHYNIZV10qg3jd2s5HuEMF6A";

    axios.delete(`/comments/${comment_id}`, {
        headers: {
            "Authorization": `Bearer ${jwt}`
        }
    })
        .then((response) => {
            node.removeChild(node.firstChild);
            node.style.height = node.offsetHeight + "px";
            node.style.transition = "height 1.6s ease, margin 1.6s ease";

            while (node.firstChild.firstChild) {
                node.firstChild.removeChild(node.firstChild.firstChild);
            }

            const amount_comments_node = document.getElementById("product-amount-comments");
            const amount_comments = Number(amount_comments_node.textContent);
            amount_comments_node.textContent = String(Number(amount_comments_node.textContent) - 1);

            const star = document.querySelector(".product-rating img");
            const rating_node = document.getElementById("product-rating");
            const rating = Number(rating_node.textContent);
            const new_rating = ((rating * amount_comments - response.data.rating) / (amount_comments - 1)).toFixed(1);
            rating_node.textContent = !isNaN(new_rating) ? new_rating : 0.0;

            if (Number(rating_node.textContent) >= 4) {
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
                node.style.overflow = "hidden";
            }, 10);

            setTimeout(() => {
                grid.removeChild(node);
            }, 1610);
        });
}