/* ==================================================
   CAREERMIND AI
   CAREER PROGRESS JAVASCRIPT
   ================================================== */


/* ==================================================
   CAREER PROGRESS DATA
   ================================================== */

const careerProgress = {

    overall: 72,

    skills: 80,

    projects: 70,

    learning: 75,

    readiness: 65

};


/* ==================================================
   GET ELEMENTS
   ================================================== */

const overallCircle =
    document.getElementById(
        "overallCircle"
    );


const overallPercentage =
    document.getElementById(
        "overallPercentage"
    );


const skillsBar =
    document.getElementById(
        "skillsBar"
    );


const projectsBar =
    document.getElementById(
        "projectsBar"
    );


const learningBar =
    document.getElementById(
        "learningBar"
    );


const readinessBar =
    document.getElementById(
        "readinessBar"
    );


const skillsPercentage =
    document.getElementById(
        "skillsPercentage"
    );


const projectsPercentage =
    document.getElementById(
        "projectsPercentage"
    );


const learningPercentage =
    document.getElementById(
        "learningPercentage"
    );


const readinessPercentage =
    document.getElementById(
        "readinessPercentage"
    );


const progressInsight =
    document.getElementById(
        "progressInsight"
    );


/* ==================================================
   UPDATE OVERALL CIRCLE
   ================================================== */

function updateOverallCircle() {

    const degree =
        careerProgress.overall * 3.6;

    if (overallCircle) {
        overallCircle.style.background = `
            conic-gradient(
                var(--accent, #5EEAD4) 0deg,
                var(--accent, #5EEAD4) ${degree}deg,
                var(--border, #232B42) ${degree}deg,
                var(--border, #232B42) 360deg
            )
        `;
    }

    if (overallPercentage) {
        overallPercentage.textContent =
            `${careerProgress.overall}%`;
    }

}


/* ==================================================
   UPDATE PROGRESS BARS
   ================================================== */

function updateProgressBars() {


    /* Skills */

    if (skillsPercentage) skillsPercentage.textContent = `${careerProgress.skills}%`;

    if (skillsBar) skillsBar.style.width = `${careerProgress.skills}%`;


    /* Projects */

    if (projectsPercentage) projectsPercentage.textContent = `${careerProgress.projects}%`;

    if (projectsBar) projectsBar.style.width = `${careerProgress.projects}%`;


    /* Learning */

    if (learningPercentage) learningPercentage.textContent = `${careerProgress.learning}%`;

    if (learningBar) learningBar.style.width = `${careerProgress.learning}%`;


    /* Career Readiness */

    if (readinessPercentage) readinessPercentage.textContent = `${careerProgress.readiness}%`;

    if (readinessBar) readinessBar.style.width = `${careerProgress.readiness}%`;

}


/* ==================================================
   CAREER INSIGHT
   ================================================== */

function updateInsight() {

    const overall =
        careerProgress.overall;


    if (overall >= 85) {

        progressInsight.textContent =
            "Excellent progress. Your skills, projects and learning activities show strong career readiness. Keep building practical experience.";

    }

    else if (overall >= 70) {

        progressInsight.textContent =
            "You are making steady progress. Continue improving your technical skills and completing practical projects to move toward stronger career readiness.";

    }

    else if (overall >= 50) {

        progressInsight.textContent =
            "You have a good foundation. Focus on strengthening your skills, completing projects and maintaining consistent learning.";

    }

    else {

        progressInsight.textContent =
            "Your career journey is just getting started. Focus on building foundational skills and gaining practical project experience.";

    }

}


/* ==================================================
   INITIALIZE
   ================================================== */

function initializeCareerProgress() {

    updateOverallCircle();

    updateProgressBars();

    updateInsight();

}


/* ==================================================
   START
   ================================================== */

initializeCareerProgress();/* ==================================================
   INTERACTIVE CAREER INSIGHT
================================================== */

const insightButton =
    document.getElementById(
        "insightButton"
    );

const insightAnalysis =
    document.getElementById(
        "insightAnalysis"
    );


const insightSkills =
    document.getElementById(
        "insightSkills"
    );

const insightProjects =
    document.getElementById(
        "insightProjects"
    );

const insightLearning =
    document.getElementById(
        "insightLearning"
    );

const insightReadiness =
    document.getElementById(
        "insightReadiness"
    );


/* ==================================================
   GENERATE INSIGHT
================================================== */

function updateDetailedInsight() {

    const skills =
        careerProgress.skills;

    const projects =
        careerProgress.projects;

    const learning =
        careerProgress.learning;

    const readiness =
        careerProgress.readiness;


    /* Skills */

    if (skills >= 80) {

        insightSkills.textContent =
            "Strong technical foundation";

    } else if (skills >= 60) {

        insightSkills.textContent =
            "Good progress; strengthen advanced skills";

    } else {

        insightSkills.textContent =
            "Focus on building core technical skills";

    }


    /* Projects */

    if (projects >= 80) {

        insightProjects.textContent =
            "Excellent practical experience";

    } else if (projects >= 60) {

        insightProjects.textContent =
            "Build more practical projects";

    } else {

        insightProjects.textContent =
            "Prioritize hands-on project experience";

    }


    /* Learning */

    if (learning >= 80) {

        insightLearning.textContent =
            "Consistent learning progress";

    } else if (learning >= 60) {

        insightLearning.textContent =
            "Maintain a regular learning routine";

    } else {

        insightLearning.textContent =
            "Increase learning consistency";

    }


    /* Career Readiness */

    if (readiness >= 80) {

        insightReadiness.textContent =
            "Strong career readiness";

    } else if (readiness >= 60) {

        insightReadiness.textContent =
            "Improve practical and professional experience";

    } else {

        insightReadiness.textContent =
            "Focus on projects and industry preparation";

    }

}


/* ==================================================
   BUTTON INTERACTION
================================================== */

if (insightButton) {

    insightButton.addEventListener(
        "click",
        function () {

            const isOpen =
                insightAnalysis.classList.contains(
                    "open"
                );


            if (isOpen) {

                insightAnalysis.classList.remove(
                    "open"
                );

                insightAnalysis.setAttribute(
                    "aria-hidden",
                    "true"
                );

                insightButton.innerHTML =
                    `View Analysis <span>→</span>`;

            } else {

                insightAnalysis.classList.add(
                    "open"
                );

                insightAnalysis.setAttribute(
                    "aria-hidden",
                    "false"
                );

                insightButton.innerHTML =
                    `Hide Analysis <span>↑</span>`;

            }

        }
    );

}


/* ==================================================
   INITIALIZE DETAILED INSIGHT & BARS
================================================== */

updateOverallCircle();
updateProgressBars();
updateDetailedInsight();