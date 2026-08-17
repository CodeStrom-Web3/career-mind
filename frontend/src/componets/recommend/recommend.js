/* ==================================================
   CAREERMIND AI
   RECOMMENDATION CARD JAVASCRIPT
   ================================================== */


/* ==================================================
   RECOMMENDATION DATA
   ================================================== */

const recommendations = [

    {
        category: "TECHNICAL SKILL",

        title: "Improve JavaScript Skills",

        description:
            "Strengthen DOM manipulation, asynchronous JavaScript and API integration to improve your frontend development capabilities.",

        reason:
            "Your current skill profile indicates that strengthening JavaScript will improve your frontend development capabilities and prepare you for more advanced applications.",

        priority: "High",

        match: 88,

        icon: "💻",

        actions: [

            "Practice DOM manipulation",

            "Build a JavaScript API project",

            "Learn asynchronous JavaScript",

            "Practice Fetch API and JSON handling"

        ]

    },


    {
        category: "PROJECT",

        title: "Build a Full-Stack Project",

        description:
            "Create a complete project that connects a frontend interface with a backend API and database.",

        reason:
            "Building a complete application will help you convert your existing frontend knowledge into practical full-stack development experience.",

        priority: "High",

        match: 84,

        icon: "🚀",

        actions: [

            "Choose a real-world problem",

            "Design the application architecture",

            "Build REST API endpoints",

            "Connect the database",

            "Deploy the project"

        ]

    },


    {
        category: "LEARNING",

        title: "Strengthen Backend Development",

        description:
            "Develop backend knowledge to complement your frontend development skills.",

        reason:
            "A stronger backend foundation can help you understand complete application architecture and improve your full-stack capabilities.",

        priority: "Medium",

        match: 76,

        icon: "⚙️",

        actions: [

            "Learn REST API concepts",

            "Practice server-side programming",

            "Learn database integration",

            "Build authentication APIs"

        ]

    },


    {
        category: "CAREER",

        title: "Build Your Project Portfolio",

        description:
            "Create and document practical projects that demonstrate your technical skills to recruiters.",

        reason:
            "A strong portfolio can demonstrate practical ability and give recruiters evidence of your technical experience.",

        priority: "Medium",

        match: 72,

        icon: "📁",

        actions: [

            "Select your best projects",

            "Add projects to GitHub",

            "Write clear project documentation",

            "Create project demonstrations"

        ]

    }

];


/* ==================================================
   GET ELEMENTS
   ================================================== */

const recommendationContainer =
    document.getElementById(
        "recommendationContainer"
    );


const recommendationCount =
    document.getElementById(
        "recommendationCount"
    );


const recommendationPage =
    document.getElementById(
        "recommendationPage"
    );


const detailsPage =
    document.getElementById(
        "recommendationDetailsPage"
    );


const backButton =
    document.getElementById(
        "backButton"
    );


const detailsIcon =
    document.getElementById(
        "detailsIcon"
    );


const detailsCategory =
    document.getElementById(
        "detailsCategory"
    );


const detailsTitle =
    document.getElementById(
        "detailsTitle"
    );


const detailsType =
    document.getElementById(
        "detailsType"
    );


const detailsPriority =
    document.getElementById(
        "detailsPriority"
    );


const detailsReason =
    document.getElementById(
        "detailsReason"
    );


const matchScore =
    document.getElementById(
        "matchScore"
    );


const circleScore =
    document.getElementById(
        "circleScore"
    );


const matchCircle =
    document.getElementById(
        "matchCircle"
    );


const actionsList =
    document.getElementById(
        "actionsList"
    );


/* ==================================================
   PRIORITY CLASS
   ================================================== */

function getPriorityClass(
    priority
) {

    return priority
        .toLowerCase();

}


/* ==================================================
   CREATE RECOMMENDATION CARD
   ================================================== */

function createRecommendationCard(
    recommendation
) {

    const card =
        document.createElement(
            "article"
        );


    card.className =
        "recommendation-card";


    card.innerHTML = `

        <div class="recommendation-card-header">

            <div class="recommendation-icon">
                ${recommendation.icon}
            </div>


            <div class="recommendation-heading">

                <span class="recommendation-category">
                    ${recommendation.category}
                </span>

                <h3 class="recommendation-card-title">
                    ${recommendation.title}
                </h3>

            </div>


            <span
                class="priority
                priority-${getPriorityClass(
                    recommendation.priority
                )}">

                ${recommendation.priority}

            </span>

        </div>


        <p class="recommendation-content">
            ${recommendation.description}
        </p>


        <div class="recommendation-card-footer">

            <div class="match-preview">

                <span>
                    Recommendation Match
                </span>

                <strong>
                    ${recommendation.match}%
                </strong>

            </div>


            <button
                class="view-recommendation-button"
                type="button">

                View Recommendation →

            </button>

        </div>

    `;


    /* ==========================================
       BUTTON
    =========================================== */

    const viewButton =
        card.querySelector(
            ".view-recommendation-button"
        );

    card.style.cursor = "pointer";

    card.addEventListener(
        "click",
        function () {
            openRecommendationDetails(
                recommendation
            );
        }
    );

    if (viewButton) {
        viewButton.addEventListener(
            "click",
            function (e) {
                e.stopPropagation();
                openRecommendationDetails(
                    recommendation
                );
            }
        );
    }


    return card;

}


/* ==================================================
   RENDER RECOMMENDATIONS
   ================================================== */

function renderRecommendations() {

    if (!recommendationContainer) return;

    recommendationContainer.innerHTML =
        "";


    recommendations.forEach(
        function (recommendation) {

            const card =
                createRecommendationCard(
                    recommendation
                );


            recommendationContainer.appendChild(
                card
            );

        }
    );

    if (recommendationCount) {
        recommendationCount.textContent =
            `${recommendations.length} Recommendations`;
    }

}


/* ==================================================
   OPEN DETAILS
   ================================================== */

function openRecommendationDetails(
    recommendation
) {

    /* ==========================================
       BASIC INFORMATION
    =========================================== */

    if (detailsIcon) detailsIcon.textContent = recommendation.icon;

    if (detailsCategory) detailsCategory.textContent = recommendation.category;

    if (detailsTitle) detailsTitle.textContent = recommendation.title;

    if (detailsType) detailsType.textContent = recommendation.category;

    if (detailsPriority) {
        detailsPriority.textContent = recommendation.priority;
        detailsPriority.className = `priority-${getPriorityClass(recommendation.priority)}`;
    }

    if (detailsReason) detailsReason.textContent = recommendation.reason;


    /* ==========================================
       MATCH SCORE
    =========================================== */

    if (matchScore) matchScore.textContent = `${recommendation.match}%`;

    if (circleScore) circleScore.textContent = `${recommendation.match}%`;


    const degree =
        recommendation.match * 3.6;


    if (matchCircle) {
        matchCircle.style.background = `
            conic-gradient(
                var(--accent, #5EEAD4) 0deg,
                var(--accent, #5EEAD4) ${degree}deg,
                var(--border, #232B42) ${degree}deg,
                var(--border, #232B42) 360deg
            )
        `;
    }


    /* ==========================================
       ACTIONS
    =========================================== */

    actionsList.innerHTML =
        "";


    recommendation.actions.forEach(
        function (action) {

            const actionItem =
                document.createElement(
                    "div"
                );


            actionItem.className =
                "action-item";


            actionItem.innerHTML = `

                <span class="action-check">
                    ✓
                </span>

                <span>
                    ${action}
                </span>

            `;


            actionsList.appendChild(
                actionItem
            );

        }
    );


    /* ==========================================
       SWITCH PAGE
    =========================================== */

    recommendationPage.style.display =
        "none";


    detailsPage.classList.add(
        "show"
    );


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* ==================================================
   BACK BUTTON
   ================================================== */

backButton.addEventListener(
    "click",
    function () {

        detailsPage.classList.remove(
            "show"
        );


        recommendationPage.style.display =
            "block";


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }
);


/* ==================================================
   ESCAPE KEY
   ================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape" &&
            detailsPage.classList.contains(
                "show"
            )
        ) {

            backButton.click();

        }

    }
);


/* ==================================================
   INITIALIZE
   ================================================== */

renderRecommendations();