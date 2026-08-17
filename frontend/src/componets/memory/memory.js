/* ==============================================
   CAREERMIND AI
   MEMORY CARD JAVASCRIPT
   ============================================== */


/* ==============================================
   MEMORY DATA
   ============================================== */

const memories = [

    {
        category: "CAREER GOAL",

        title: "Career Direction",

        content:
            "Working toward building a strong career in software development and improving practical technical skills.",

        importance: 85,

        strength: 75,

        relevance: 90,

        updated: "Recently",

        icon: "🎯"
    },


    {
        category: "TECHNICAL SKILL",

        title: "Web Development",

        content:
            "Currently working with HTML, CSS and JavaScript to build interactive frontend applications.",

        importance: 80,

        strength: 78,

        relevance: 88,

        updated: "Recently",

        icon: "💻"
    },


    {
        category: "PROGRAMMING",

        title: "Java Development",

        content:
            "Learning Java programming concepts including object-oriented programming, classes, methods and collections.",

        importance: 75,

        strength: 70,

        relevance: 82,

        updated: "Recently",

        icon: "☕"
    },


    {
        category: "PROJECT",

        title: "Frontend Development",

        content:
            "Currently building reusable frontend components for a CareerMind AI project.",

        importance: 90,

        strength: 82,

        relevance: 95,

        updated: "Recently",

        icon: "🚀"
    }

];


/* ==============================================
   GET ELEMENTS
   ============================================== */

const memoryPage =
    document.getElementById("memoryPage");

const memoryContainer =
    document.getElementById(
        "memoryContainer"
    );

const memoryCount =
    document.getElementById(
        "memoryCount"
    );

const detailsPage =
    document.getElementById(
        "memoryDetailsPage"
    );

const backButton =
    document.getElementById(
        "backButton"
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

const detailsUpdated =
    document.getElementById(
        "detailsUpdated"
    );

const detailsContent =
    document.getElementById(
        "detailsContent"
    );

const analysisScore =
    document.getElementById(
        "analysisScore"
    );

const circlePercentage =
    document.getElementById(
        "circlePercentage"
    );

const memoryCircle =
    document.getElementById(
        "memoryCircle"
    );

const importanceBar =
    document.getElementById(
        "importanceBar"
    );

const strengthBar =
    document.getElementById(
        "strengthBar"
    );

const relevanceBar =
    document.getElementById(
        "relevanceBar"
    );

const importanceValue =
    document.getElementById(
        "importanceValue"
    );

const strengthValue =
    document.getElementById(
        "strengthValue"
    );

const relevanceValue =
    document.getElementById(
        "relevanceValue"
    );


/* ==============================================
   IMPORTANCE LABEL
   ============================================== */

function getImportanceLabel(value) {

    if (value >= 80) {

        return "High";

    }

    if (value >= 60) {

        return "Medium";

    }

    return "Low";

}


/* ==============================================
   CREATE MEMORY CARD
   ============================================== */

function createMemoryCard(memory) {

    const card =
        document.createElement(
            "article"
        );


    card.className =
        "memory-card";


    card.innerHTML = `

        <div class="memory-card-header">

            <div class="memory-icon">
                ${memory.icon}
            </div>


            <div class="memory-card-heading">

                <span class="memory-category">
                    ${memory.category}
                </span>

                <h3 class="memory-card-title">
                    ${memory.title}
                </h3>

            </div>


            <span
                class="memory-importance
                ${getImportanceLabel(
                    memory.importance
                ).toLowerCase()}">

                ${getImportanceLabel(
                    memory.importance
                )}

            </span>

        </div>


        <p class="memory-card-content">
            ${memory.content}
        </p>


        <div class="memory-card-footer">

            <span class="memory-updated">
                Updated ${memory.updated}
            </span>


            <button
                class="view-memory-button"
                type="button">

                View Memory →

            </button>

        </div>

    `;


    /* ==========================================
       VIEW MEMORY
    =========================================== */

    const viewButton =
        card.querySelector(
            ".view-memory-button"
        );

    card.style.cursor = "pointer";

    card.addEventListener(
        "click",
        function () {
            openMemoryDetails(
                memory
            );
        }
    );

    if (viewButton) {
        viewButton.addEventListener(
            "click",
            function (e) {
                e.stopPropagation();
                openMemoryDetails(
                    memory
                );
            }
        );
    }


    return card;

}


/* ==============================================
   RENDER MEMORIES
   ============================================== */

function renderMemories() {

    if (!memoryContainer) return;

    memoryContainer.innerHTML =
        "";


    memories.forEach(
        function (memory) {

            const card =
                createMemoryCard(
                    memory
                );


            memoryContainer.appendChild(
                card
            );

        }
    );

    if (memoryCount) {
        memoryCount.textContent =
            `${memories.length} Memories`;
    }

}


/* ==============================================
   OPEN DETAILS
   ============================================== */

function openMemoryDetails(memory) {

    /* ==========================================
       UPDATE INFORMATION
    =========================================== */

    if (detailsCategory) detailsCategory.textContent = memory.category;

    if (detailsTitle) detailsTitle.textContent = memory.title;

    if (detailsType) detailsType.textContent = memory.category;

    if (detailsUpdated) detailsUpdated.textContent = memory.updated;

    if (detailsContent) detailsContent.textContent = memory.content;


    /* ==========================================
       UPDATE VALUES
    =========================================== */

    if (analysisScore) analysisScore.textContent = `${memory.importance}%`;

    if (circlePercentage) circlePercentage.textContent = `${memory.importance}%`;

    if (importanceValue) importanceValue.textContent = `${memory.importance}%`;

    if (strengthValue) strengthValue.textContent = `${memory.strength}%`;

    if (relevanceValue) relevanceValue.textContent = `${memory.relevance}%`;


    /* ==========================================
       UPDATE CIRCULAR GRAPH (PIE CHART)
    =========================================== */

    const degree =
        memory.importance * 3.6;


    if (memoryCircle) {
        memoryCircle.style.background = `
            conic-gradient(
                var(--accent, #5EEAD4) 0deg,
                var(--accent, #5EEAD4) ${degree}deg,
                var(--border, #232B42) ${degree}deg,
                var(--border, #232B42) 360deg
            )
        `;
    }


    /* ==========================================
       RESET BARS
    =========================================== */

    if (importanceBar) importanceBar.style.width = "0%";

    if (strengthBar) strengthBar.style.width = "0%";

    if (relevanceBar) relevanceBar.style.width = "0%";


    /* ==========================================
       SWITCH PAGE / SHOW MODAL
    =========================================== */

    if (memoryPage) {
        memoryPage.style.display = "none";
    }

    if (detailsPage) {
        detailsPage.classList.add("show");
    }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });


    /* ==========================================
       ANIMATE GRAPH BARS
    =========================================== */

    setTimeout(
        function () {

            if (importanceBar) importanceBar.style.width = `${memory.importance}%`;

            if (strengthBar) strengthBar.style.width = `${memory.strength}%`;

            if (relevanceBar) relevanceBar.style.width = `${memory.relevance}%`;

        },
        100
    );

}


/* ==============================================
   BACK BUTTON
   ============================================== */

if (backButton) {
    backButton.addEventListener(
        "click",
        function () {

            if (detailsPage) {
                detailsPage.classList.remove("show");
            }

            if (memoryPage) {
                memoryPage.style.display = "block";
            }

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        }
    );
}


/* ==============================================
   ESC KEY
   ============================================== */

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


/* ==============================================
   INITIALIZE
   ============================================== */

renderMemories();