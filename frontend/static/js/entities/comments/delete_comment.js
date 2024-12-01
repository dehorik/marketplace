function delete_comment(node, comment_id) {
    node.removeEventListener("click", delete_comment);

    node.style.height = node.offsetHeight + "px";
    node.classList.add("deleted-comment");

    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }

    const jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJpYXQiOjE3MzMwNzE1NDYsImV4cCI6MTczMzE2MTU0Nn0.l4WW1Rh8QdZtVsHAiR_IVZalKk6H3YZlMY4N1ueIt6qZHW02wH-Whh8n4k1sZWqJQHZnUvDIsD-GgQtKxviFMLvXcCUgkFSYjLkQ02LhPxVQ68VFIvaqxLV9fJAzIqEJ4XvsNgRnfvgWLuUdHaPNLe5huXjJpI1jSfddMcZ9DwfsYQuCJi7548wbZHfGRZLRXJhmrSdAC5LqEOdQbSy1G46HGZHIx4uGc4cDTECfmU-YSzhq3bOTfyHh5izId-ZCrM_PV6Ka7Uc-6PwjYEkhhIzEEeMyZXToYoKn-5brxeqJOrJA2ZFEN1XwS7H0Nbswu6BOyb6u8MXFb5UNyLsu-Q";
    axios({
        url: `/comments/${comment_id}`,
        method: "delete",
        headers: {
            "Authorization": `Bearer ${jwt}`
        }
    })
        .then(() => {
            setTimeout(() => {
                node.style.height = "0";
                node.style.margin = "0";
            }, 10);

            setTimeout(() => {
                grid.removeChild(node);

                if (grid.querySelectorAll(".comment").length === 0) {
                    const message_area = document.createElement("div");
                    message_area.className = "comments-message";
                    message_area.textContent = "Отзывы не найдены. Вы можете стать первым, кто оценит товар.";

                    grid.append(message_area);
                }
            }, 1600);

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
        })
        .catch(() => {
           const deletion_error = document.createElement("div");
           const deletion_error_message = document.createElement("span");
           deletion_error.className = "comment-deletion-error";
           deletion_error_message.textContent = "Ошибка удаления отзыва";
           deletion_error.append(deletion_error_message);

           node.append(deletion_error);
        });
}
