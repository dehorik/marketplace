function delete_comment(node, comment_id) {
    node.removeEventListener("click", delete_comment);

    node.style.height = node.offsetHeight + "px";
    node.classList.add("deleted-comment");

    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }

    axios({
        url: `/comments/${comment_id}`,
        method: "delete",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    })
        .then(() => {
            setTimeout(() => {
                node.style.height = "0";
                node.style.margin = "0";
            }, 10);

            setTimeout(() => {
                grid.removeChild(node);
                recalculate_product_rating();

                if (grid.querySelectorAll(".comment").length === 0) {
                    const message_area = document.createElement("div");
                    message_area.className = "comments-message";
                    message_area.textContent = "Отзывы не найдены. Вы можете стать первым, кто оценит товар.";

                    grid.append(message_area);
                }
            }, 1600);
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
