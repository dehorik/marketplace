window.addEventListener("load", () => {
    const auth_btn = document.querySelector(".auth-btn");

    if (getToken()) {
        auth_btn.href = "/users/me/home";
    }
    else {
        auth_btn.href = "/auth/form?redirect_url=/users/me/home";
    }
})
