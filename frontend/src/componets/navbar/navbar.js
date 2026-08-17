/* ==================================================
   CAREERMIND AI
   NAVBAR JAVASCRIPT
   ================================================== */


/* ==================================================
   GET ELEMENTS
   ================================================== */

const notificationBtn =
    document.getElementById("notificationBtn");

const notificationBadge =
    document.getElementById("notificationBadge");

const profileDropdownBtn =
    document.getElementById("profileDropdownBtn");

const profileMenu =
    document.getElementById("profileMenu");

const logoutBtn =
    document.getElementById("logoutBtn");


/* ==================================================
   NOTIFICATION
   ================================================== */

if (notificationBtn) {

    notificationBtn.addEventListener(
        "click",
        function () {

            /*
             * Demo notification behaviour.
             * Later this can be replaced with
             * real backend notifications.
             */

            alert(
                "You have 2 new notifications."
            );


            /*
             * Hide notification count
             */

            if (notificationBadge) {

                notificationBadge.style.display =
                    "none";

            }

        }
    );

}


/* ==================================================
   PROFILE DROPDOWN
   ================================================== */

if (profileDropdownBtn) {

    profileDropdownBtn.addEventListener(
        "click",
        function (event) {

            /*
             * Prevent click from reaching
             * document click listener.
             */

            event.stopPropagation();


            /*
             * Toggle dropdown
             */

            profileMenu.classList.toggle("show");


            /*
             * Toggle profile button state
             */

            profileDropdownBtn.classList.toggle(
                "active"
            );


            /*
             * Update accessibility attribute
             */

            const isOpen =
                profileMenu.classList.contains("show");


            profileDropdownBtn.setAttribute(
                "aria-expanded",
                isOpen
            );

        }
    );

}


/* ==================================================
   CLOSE PROFILE MENU
   WHEN CLICKING OUTSIDE
   ================================================== */

document.addEventListener(
    "click",
    function (event) {

        if (
            profileMenu &&
            profileDropdownBtn &&
            !profileDropdownBtn.contains(event.target) &&
            !profileMenu.contains(event.target)
        ) {

            profileMenu.classList.remove("show");

            profileDropdownBtn.classList.remove(
                "active"
            );

            profileDropdownBtn.setAttribute(
                "aria-expanded",
                "false"
            );

        }

    }
);


/* ==================================================
   ESC KEY
   CLOSE DROPDOWN
   ================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            if (profileMenu) {

                profileMenu.classList.remove(
                    "show"
                );

            }


            if (profileDropdownBtn) {

                profileDropdownBtn.classList.remove(
                    "active"
                );

                profileDropdownBtn.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }

        }

    }
);


/* ==================================================
   LOGOUT
   ================================================== */

if (logoutBtn) {

    logoutBtn.addEventListener(
        "click",
        function () {

            const confirmLogout =
                confirm(
                    "Are you sure you want to logout?"
                );


            if (confirmLogout) {

                /*
                 * Clear login information later
                 * when authentication is connected.
                 */

                localStorage.removeItem(
                    "careerMindUser"
                );


                /*
                 * Redirect to landing page on logout
                 */

                let targetLanding = "landing.html";
                if (window.location.pathname.includes("/componets/")) {
                    targetLanding = "../../pages/landing.html";
                }

                window.location.href = targetLanding;

            }

        }
    );

}