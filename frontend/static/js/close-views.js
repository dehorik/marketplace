let reviewsOp = document.getElementById('reviewsOp');
let reviews = document.querySelector(".reviews-main");
let reviewsCl  = document.getElementById("close-reviews");

reviewsOp.onclick = () => {
    reviews.classList.add("active");
};

reviewsCl.onclick = () => {
    reviews.classList.remove("active");
};