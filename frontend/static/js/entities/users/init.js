window.addEventListener("load", () => {
    getVerifiedToken().then((token) => {
       axios({
           url: "/users/me",
           method: "get",
           headers: {
               Authorization: `Bearer ${token}`
           }
       })
           .then((response) => {
               const user_photo = document.querySelector(".user-page_user-photo img");
               const username = document.querySelector(".user-page_username span");
               const email = document.querySelector(".user-page_email span");
               const registration_date = document.querySelector(".user-page_registration-date span");

               if (response.data.photo_path) {
                   user_photo.src = response.data.photo_path;
               }
               else {
                   user_photo.src = "/static/img/default-avatar.png";
               }

               username.textContent = response.data.username;

               if (response.data.email) {
                   email.textContent = response.data.email;
               }
               else {
                   email.textContent = "Почта не привязана";
               }

               registration_date.textContent = response.data.registration_date;

               const logout_button = document.querySelector(".user-page_logout-btn a");
               logout_button.addEventListener("click", logout);

               if (response.data.role_id >= 2) {
                   const navbar = document.querySelector(".user-page_navbar");

                   const divElement = document.createElement("div");
                   const aElement = document.createElement("a");
                   const spanElement = document.createElement("span");

                   spanElement.textContent = "Панель управления";
                   aElement.appendChild(spanElement);
                   divElement.appendChild(aElement);
                   navbar.appendChild(divElement);
               }
           })
           .catch(() => {
               window.location.href = "/auth/form";
           });
    });
});
