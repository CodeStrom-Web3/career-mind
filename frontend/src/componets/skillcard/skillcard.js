/* ==================================================
   CAREERMIND AI
   SKILL CARD JAVASCRIPT
   ================================================== */


/* ==================================================
   YOUR SKILL DATA
   ================================================== */

/*
    These are the technologies you have mentioned
    working with / learning.

    Change ONLY the percentage and level when
    you want to update your actual proficiency.
*/

const skills = [

    {
        name: "HTML",
        percentage: 85,
        level: "Advanced"
    },

    {
        name: "CSS",
        percentage: 80,
        level: "Intermediate"
    },

    {
        name: "JavaScript",
        percentage: 70,
        level: "Intermediate"
    },

    {
        name: "Java",
        percentage: 75,
        level: "Intermediate"
    },

    {
        name: "C++",
        percentage: 65,
        level: "Intermediate"
    }

];


/* ==================================================
   ELEMENTS
   ================================================== */

const skillsPage =
    document.getElementById("skillsPage");

const skillsContainer =
    document.getElementById("skillsContainer");

const skillsCount =
    document.getElementById("skillsCount");

const skillDetailsPage =
    document.getElementById("skillDetailsPage");

const backButton =
    document.getElementById("backButton");

const detailsSkillName =
    document.getElementById("detailsSkillName");

const detailsDescription =
    document.getElementById("detailsDescription");

const detailsLevel =
    document.getElementById("detailsLevel");

const detailsProficiency =
    document.getElementById("detailsProficiency");

const detailsStatus =
    document.getElementById("detailsStatus");

const chartPercentage =
    document.getElementById("chartPercentage");

const piePercentage =
    document.getElementById("piePercentage");

const pieChart =
    document.getElementById("pieChart");

const legendProficiency =
    document.getElementById("legendProficiency");

const legendRemaining =
    document.getElementById("legendRemaining");


/* ==================================================
   STATUS FUNCTION
   ================================================== */

function getSkillStatus(percentage) {

    if (percentage >= 80) {

        return "Strong skill";

    }

    if (percentage >= 60) {

        return "Good progress";

    }

    if (percentage >= 40) {

        return "Needs improvement";

    }

    return "Beginner level";

}


/* ==================================================
   LEVEL CLASS
   ================================================== */

function getLevelClass(level) {

    return level
        .toLowerCase()
        .replace(/\s+/g, "-");

}


/* ==================================================
   CREATE SKILL CARD
   ================================================== */

function createSkillCard(skill, index) {

    const card =
        document.createElement("article");

    card.className =
        "skill-card";


    card.innerHTML = `

        <div class="skill-header">

            <div>

                <span class="skill-category">
                    TECHNICAL SKILL
                </span>

                <h3 class="skill-name">
                    ${skill.name}
                </h3>

            </div>

            <span
                class="skill-level ${getLevelClass(skill.level)}">

                ${skill.level}

            </span>

        </div>


        <div class="skill-progress-info">

            <span>
                Proficiency
            </span>

            <strong>
                ${skill.percentage}%
            </strong>

        </div>


        <div class="skill-progress-track">

            <div
                class="skill-progress-fill"
                data-progress="${skill.percentage}">
            </div>

        </div>


        <div class="skill-footer">

            <span class="skill-status">

                ${getSkillStatus(skill.percentage)}

            </span>


            <button
                class="skill-details-btn"
                type="button">

                View details →

            </button>

        </div>

    `;


    /* =========================================
       PROGRESS ANIMATION
    ========================================== */

    setTimeout(function () {

        const progress =
            card.querySelector(
                ".skill-progress-fill"
            );

        progress.style.width =
            skill.percentage + "%";

    }, 100 + (index * 100));


    /* =========================================
       VIEW DETAILS
    ========================================== */

    const detailsButton =
        card.querySelector(
            ".skill-details-btn"
        );

    card.style.cursor = "pointer";

    card.addEventListener(
        "click",
        function () {
            openSkillDetails(skill);
        }
    );

    if (detailsButton) {
        detailsButton.addEventListener(
            "click",
            function (e) {
                e.stopPropagation();
                openSkillDetails(skill);
            }
        );
    }


    return card;

}


/* ==================================================
   RENDER ALL SKILLS
   ================================================== */

function renderSkills() {

    if (!skillsContainer) {

        return;

    }


    skillsContainer.innerHTML = "";


    skills.forEach(
        function (skill, index) {

            const card =
                createSkillCard(
                    skill,
                    index
                );

            skillsContainer.appendChild(
                card
            );

        }
    );


    if (skillsCount) {

        skillsCount.textContent =
            `${skills.length} Skills`;

    }

}


/* ==================================================
   OPEN DETAILS
   ================================================== */

function openSkillDetails(skill) {

    const percentage =
        Math.max(
            0,
            Math.min(
                100,
                skill.percentage
            )
        );


    const remaining =
        100 - percentage;


    /* =========================================
       UPDATE TEXT
    ========================================== */

    if (detailsSkillName) detailsSkillName.textContent = skill.name;

    if (detailsDescription) detailsDescription.textContent = `Interactive proficiency analysis for ${skill.name}.`;

    if (detailsLevel) detailsLevel.textContent = skill.level;

    if (detailsProficiency) detailsProficiency.textContent = `${percentage}%`;

    if (detailsStatus) detailsStatus.textContent = getSkillStatus(percentage);

    if (chartPercentage) chartPercentage.textContent = `${percentage}%`;

    if (piePercentage) piePercentage.textContent = `${percentage}%`;

    if (legendProficiency) legendProficiency.textContent = `${percentage}%`;

    if (legendRemaining) legendRemaining.textContent = `${remaining}%`;


    /* =========================================
       CREATE PIE CHART
    ========================================== */

    const degree =
        percentage * 3.6;


    if (pieChart) {
        pieChart.style.background = `
            conic-gradient(
                var(--accent, #5EEAD4) 0deg,
                var(--accent, #5EEAD4) ${degree}deg,
                var(--border, #232B42) ${degree}deg,
                var(--border, #232B42) 360deg
            )
        `;
    }


    /* =========================================
       SHOW DETAILS PAGE
    ========================================== */

    if (skillsPage) {
        skillsPage.style.display = "none";
    }

    if (skillDetailsPage) {
        skillDetailsPage.classList.add("show");
        skillDetailsPage.setAttribute("aria-hidden", "false");
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* ==================================================
   BACK TO SKILLS
   ================================================== */

if (backButton) {

    backButton.addEventListener(
        "click",
        function () {

            if (skillDetailsPage) {
                skillDetailsPage.classList.remove("show");
                skillDetailsPage.setAttribute("aria-hidden", "true");
            }

            if (skillsPage) {
                skillsPage.style.display = "block";
            }


            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        }
    );

}


/* ==================================================
   ESC KEY
   ================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape" &&
            skillDetailsPage.classList.contains("show")
        ) {

            backButton.click();

        }

    }
);


/* ==================================================
   START
   ================================================== */

renderSkills();