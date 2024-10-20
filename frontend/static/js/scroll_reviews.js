const comments_area = document.querySelector(".st5_29");

window.addEventListener('load', () => {
    State.deleteFromStorage();
    const state_data = new ReviewsStateData();
    const state = new State(state_data);
    state.saveToStorage();

    update_comments();
    window.addEventListener('scroll', check_position);
});

function updateReviews(amount = 10) {
    const state = get_state_obj();

    let url = "/comments/latest";
    let params = {
        amount: amount,
        product_id: state.data.product_id,
        last_comment_id: state.data.last_comment_id
    };


    axios.get(url, {params})
        .then(function (response) {
            let comments = response.data.comments;
            if   (comments.length !== 0) {
                state.data.last_comment_id = comments.slice(-1)[0].comment_id;
                state.saveToStorage();

                for (let i in comments) {
                    placeReview(createComment(comments[i]));
                }
            }
        });
}


function createComment(comment) {
    const commentElement = document.createElement('div');
    commentElement.className = 'w1q_29';
    commentElement.dataset.reviewUuid = comment.comment_id;

    // Author block
    const authorBlock = document.createElement('div');
    authorBlock.className = 'qw2_29';

    const authorInfo = document.createElement('div');
    authorInfo.className = 'sq6_29 s6q_29';

    const authorImage = document.createElement('div');
    authorImage.className = 'p5y_29 py6_29 yp5_29 qs7_29';
    const authorImg = document.createElement('img');
    authorImg.loading = 'lazy';
    authorImg.fetchpriority = 'low';
    authorImg.src = comment.author_avatar_url;
    authorImg.srcset = `${comment.author_avatar_url} 2x`;
    authorImg.className = 'py7_29 b921-a';
    authorImage.appendChild(authorImg);

    const authorName = document.createElement('div');
    const authorNameSpan = document.createElement('span');
    authorNameSpan.className = 'sq7_29';
    authorNameSpan.textContent = comment.author_name;
    authorName.appendChild(authorNameSpan);

    authorInfo.appendChild(authorImage);
    authorInfo.appendChild(authorName);

    const dateBlock = document.createElement('div');
    dateBlock.className = 'v4q_29';

    const date = document.createElement('div');
    date.className = 'qv5_29';
    date.textContent = comment.published_at; // Assuming you have a formatted date

    const ratingBlock = document.createElement('div');
    ratingBlock.className = 'vq5_29';

    const ratingStars = createRatingStars(comment.rating);
    ratingBlock.appendChild(ratingStars);

    dateBlock.appendChild(date);
    dateBlock.appendChild(ratingBlock);

    authorBlock.appendChild(authorInfo);
    authorBlock.appendChild(dateBlock);

    // Content block
    const contentBlock = document.createElement('div');
    contentBlock.className = 'wq2_29';

    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'w3q_29';

    const content = document.createElement('div');
    content.textContent = comment.content;

    contentWrapper.appendChild(content);
    contentBlock.appendChild(contentWrapper);

    // Actions block
    const actionsBlock = document.createElement('div');
    actionsBlock.className = 'vq9_29 q2w_29';

    const actionsWrapper = document.createElement('div');
    actionsWrapper.className = 'qv8_29';

    const likeButton = document.createElement('div');
    likeButton.className = 'q8v_29';

    const likeButtonWrapper = document.createElement('div');
    likeButtonWrapper.className = 'd4015-a';

    const likeButtonElement = document.createElement('button');
    likeButtonElement.className = 'sq5_29 ag017-a0 ag017-a2';
    likeButtonElement.fill = true;

    const likeIcon = document.createElement('svg');
    likeIcon.xmlns = 'http://www.w3.org/2000/svg';
    likeIcon.width = '24';
    likeIcon.height = '24';
    likeIcon.className = 'ag017-b1';

    const likePath = document.createElement('path');
    likePath.fill = 'currentColor';
    likePath.d = 'M5 10a2 2 0 1 1 0 4 2 2 0 0 1 0-4m14 0a2 2 0 1 1 0 4 2 2 0 0 1 0-4m-5 2a2 2 0 1 0-4 0 2 2 0 0 0 4 0';
    likeIcon.appendChild(likePath);

    likeButtonElement.appendChild(likeIcon);

    likeButtonWrapper.appendChild(likeButtonElement);
    likeButton.appendChild(likeButtonWrapper);

    actionsWrapper.appendChild(likeButton);
    actionsBlock.appendChild(actionsWrapper);

    // Assemble the comment element
    commentElement.appendChild(authorBlock);
    commentElement.appendChild(contentBlock);
    commentElement.appendChild(actionsBlock);

    return commentElement;
}

function createRatingStars(rating) {
    const ratingElement = document.createElement('div');
    ratingElement.className = 'a5d16-a a5d16-a0';

    for (let i = 0; i < rating; i++) {
        const star = document.createElement('svg');
        star.xmlns = 'http://www.w3.org/2000/svg';
        star.width = '20';
        star.height = '20';
        star.viewBox = '0 0 24 24';
        star.style.color = 'rgb(255, 168, 0)';

        const starPath = document.createElement('path');
        starPath.fill = 'currentColor';
        starPath.d = 'M9.358 6.136C10.53 4.046 11.117 3 12 3s1.47 1.045 2.643 3.136c.259.462.484 1.038.925 1.354.42.302 1.006.332 1.502.422 2.356.429 3.534.643 3.842 1.457q.034.09.057.182c.208.847-.632 1.581-2.316 3.313-.527.541-.766.798-.872 1.149-.097.325-.05.677.044 1.381.323 2.42.482 3.762-.21 4.31-1.24.98-3.24-.742-4.359-1.259C12.638 18.16 12.33 18 12 18s-.638.16-1.256.445c-1.12.517-3.119 2.24-4.358 1.258-.693-.547-.528-1.889-.205-4.309.094-.704.14-1.056.043-1.381-.105-.351-.345-.607-.872-1.15-1.684-1.73-2.529-2.465-2.32-3.312q.021-.093.056-.182c.308-.814 1.486-1.028 3.842-1.457.496-.09 1.083-.12 1.502-.422.441-.316.666-.893.926-1.354';
        star.appendChild(starPath);

        ratingElement.appendChild(star);
    }

    return ratingElement;
}

function placeReview(reviewElement) {
    comments_area.appendChild(reviewElement);
}


function checkPosition() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollPosition = window.scrollY;

    if (documentHeight - (windowHeight + scrollPosition) <= 170) {
        updateReviews();

        window.removeEventListener('scroll', checkPosition);
        setTimeout(() => {
            window.addEventListener('scroll', checkPosition);
        }, 200);
    }
}