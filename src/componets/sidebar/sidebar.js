/* ==================================================
   CAREERMIND AI
   SIDEBAR JAVASCRIPT
   ================================================== */


/* ==================================================
   ELEMENTS
   ================================================== */

const sidebar =
    document.getElementById("sidebar");

const sidebarCollapse =
    document.getElementById("sidebarCollapse");

const sidebarItems =
    document.querySelectorAll(".sidebar-item");


/* ==================================================
   ACTIVE PAGE
   ================================================== */

/*
   Get the current page filename.

   Example:

   dashboard.html
   career-profile.html
   roadmap.html
*/

const currentPage =
    window.location.pathname
        .split("/")
        .pop()
        .replace(".html", "");


/*
   Find matching sidebar item.
*/

sidebarItems.forEach(function (item) {

    const page =
        item.getAttribute("data-page");


    /*
       Remove default active class
       first.
    */

    item.classList.remove("active");


    /*
       Compare current page
       with data-page.
    */

    if (page === currentPage) {

        item.classList.add("active");

    }

});


/* ==================================================
   SIDEBAR NAVIGATION
   ================================================== */

sidebarItems.forEach(function (item) {

    item.addEventListener(
        "click",
        function () {

            /*
             * Remove active from
             * every item.
             */

            sidebarItems.forEach(
                function (navItem) {

                    navItem.classList.remove(
                        "active"
                    );

                }
            );


            /*
             * Add active to clicked item.
             */

            item.classList.add("active");

        }
    );

});


/* ==================================================
   COLLAPSE SIDEBAR
   ================================================== */

if (sidebarCollapse) {

    sidebarCollapse.addEventListener(
        "click",
        function () {

            /*
             * Toggle collapsed state.
             */

            sidebar.classList.toggle(
                "collapsed"
            );


            /*
             * Find main content.
             */

            const mainContent =
                document.querySelector(
                    ".main-content"
                );


            /*
             * Update main content
             * position.
             */

            if (mainContent) {

                mainContent.classList.toggle(
                    "sidebar-collapsed"
                );

            }


            /*
             * Change collapse icon.
             */

            const collapseIcon =
                sidebarCollapse
                    .querySelector(
                        "span:first-child"
                    );


            if (
                sidebar.classList.contains(
                    "collapsed"
                )
            ) {

                collapseIcon.textContent = "»";

            } else {

                collapseIcon.textContent = "«";

            }

        }
    );

}


/* ==================================================
   MOBILE SIDEBAR
   ================================================== */

function openMobileSidebar() {

    if (window.innerWidth <= 768) {

        sidebar.classList.add(
            "mobile-open"
        );

    }

}


function closeMobileSidebar() {

    sidebar.classList.remove(
        "mobile-open"
    );

}


/* ==================================================
   CLOSE MOBILE SIDEBAR
   AFTER NAVIGATION
   ================================================== */

sidebarItems.forEach(function (item) {

    item.addEventListener(
        "click",
        function () {

            if (window.innerWidth <= 768) {

                closeMobileSidebar();

            }

        }
    );

});


/* ==================================================
   ESC KEY
   ================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            closeMobileSidebar();

        }

    }
);