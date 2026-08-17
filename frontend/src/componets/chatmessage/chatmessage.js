/* ==================================================
   CAREERMIND AI
   CHAT MESSAGE JAVASCRIPT
   ================================================== */


/* ==================================================
   ELEMENTS
   ================================================== */

const chatMessages =
    document.getElementById(
        "chatMessages"
    );


const chatInput =
    document.getElementById(
        "chatInput"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const typingContainer =
    document.getElementById(
        "typingContainer"
    );


const clearChatButton =
    document.getElementById(
        "clearChatButton"
    );


/* ==================================================
   DEMO AI RESPONSES
   ================================================== */

const aiResponses = [

    "Based on your current skills, I recommend strengthening JavaScript and building more practical frontend projects. 🚀",

    "Your career progress looks promising. Focus on improving your project experience and building a strong portfolio.",

    "A good next step would be to learn REST APIs and connect your frontend applications with a backend.",

    "You can improve your career readiness by combining technical learning with practical projects and GitHub contributions.",

    "Based on your development journey, consistency is important. Try setting a weekly learning goal and tracking your progress."

];


/* ==================================================
   GET CURRENT TIME
   ================================================== */

function getCurrentTime() {

    const now =
        new Date();


    return now.toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


/* ==================================================
   CREATE MESSAGE
   ================================================== */

function createMessage(
    message,
    sender
) {

    const messageRow =
        document.createElement(
            "div"
        );


    messageRow.classList.add(
        "message-row",
        "new-message"
    );


    /* ==========================================
       AI MESSAGE
    =========================================== */

    if (sender === "ai") {

        messageRow.classList.add(
            "ai-row"
        );


        messageRow.innerHTML = `

            <div class="message-avatar">
                🧠
            </div>

            <div class="message-content">

                <div class="message-info">

                    <strong>
                        CareerMind AI
                    </strong>

                    <span>
                        ${getCurrentTime()}
                    </span>

                </div>

                <div class="message-bubble ai-bubble">

                    <p>
                        ${escapeHTML(message)}
                    </p>

                </div>

            </div>

        `;

    }


    /* ==========================================
       USER MESSAGE
    =========================================== */

    else {

        messageRow.classList.add(
            "user-row"
        );


        messageRow.innerHTML = `

            <div class="message-content">

                <div class="message-info user-info">

                    <span>
                        ${getCurrentTime()}
                    </span>

                    <strong>
                        You
                    </strong>

                </div>

                <div class="message-bubble user-bubble">

                    <p>
                        ${escapeHTML(message)}
                    </p>

                </div>

            </div>

        `;

    }


    chatMessages.appendChild(
        messageRow
    );


    scrollToBottom();

}


/* ==================================================
   ESCAPE HTML
================================================== */

function escapeHTML(
    text
) {

    const element =
        document.createElement(
            "div"
        );


    element.textContent =
        text;


    return element.innerHTML;

}


/* ==================================================
   GET AI RESPONSE
   ================================================== */

function getAIResponse(
    userMessage
) {

    const message =
        userMessage.toLowerCase();


    /* Specific demo responses */

    if (
        message.includes(
            "skill"
        )
    ) {

        return "You should focus on strengthening your existing skills while adding one new skill at a time. Practical projects are the best way to demonstrate your progress.";

    }


    if (
        message.includes(
            "javascript"
        )
    ) {

        return "For JavaScript, focus on DOM manipulation, asynchronous programming, Fetch API, ES6+ features and building practical projects.";

    }


    if (
        message.includes(
            "career"
        )
    ) {

        return "Your career development should combine technical skills, practical projects, communication and a strong portfolio.";

    }


    if (
        message.includes(
            "project"
        )
    ) {

        return "Try building a project that solves a real problem. Connect the frontend to an API and database so you can demonstrate complete application development.";

    }


    /* Random general response */

    const randomIndex =
        Math.floor(
            Math.random() *
            aiResponses.length
        );


    return aiResponses[
        randomIndex
    ];

}


/* ==================================================
   SHOW TYPING
   ================================================== */

function showTyping() {

    typingContainer.classList.add(
        "show"
    );


    scrollToBottom();

}


/* ==================================================
   HIDE TYPING
   ================================================== */

function hideTyping() {

    typingContainer.classList.remove(
        "show"
    );

}


/* ==================================================
   SEND MESSAGE
   ================================================== */

function sendMessage() {

    const message =
        chatInput.value.trim();


    /* Do nothing for empty message */

    if (!message) {

        return;

    }


    /* Add user message */

    createMessage(
        message,
        "user"
    );


    /* Clear input */

    chatInput.value =
        "";


    autoResizeInput();


    /* Disable button */

    sendButton.disabled =
        true;


    /* Show AI typing */

    showTyping();


    /* Demo AI response */

    setTimeout(
        function () {

            hideTyping();


            const response =
                getAIResponse(
                    message
                );


            createMessage(
                response,
                "ai"
            );


            sendButton.disabled =
                false;


            chatInput.focus();

        },
        1200
    );

}


/* ==================================================
   SCROLL TO BOTTOM
   ================================================== */

function scrollToBottom() {

    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* ==================================================
   AUTO RESIZE TEXTAREA
   ================================================== */

function autoResizeInput() {

    chatInput.style.height =
        "auto";


    chatInput.style.height =
        Math.min(
            chatInput.scrollHeight,
            120
        ) + "px";

}


/* ==================================================
   SEND BUTTON
   ================================================== */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* ==================================================
   ENTER TO SEND
   ================================================== */

chatInput.addEventListener(
    "keydown",
    function (event) {

        /*
           Enter = Send
           Shift + Enter = New line
        */

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


/* ==================================================
   TEXTAREA RESIZE
   ================================================== */

chatInput.addEventListener(
    "input",
    autoResizeInput
);


/* ==================================================
   CLEAR CHAT
   ================================================== */

clearChatButton.addEventListener(
    "click",
    function () {

        const confirmed =
            confirm(
                "Clear the current conversation?"
            );


        if (!confirmed) {

            return;

        }


        chatMessages.innerHTML = "";


        /* Add fresh welcome message */

        createMessage(
            "Hello! 👋 I'm your CareerMind AI assistant. How can I help you with your career today?",
            "ai"
        );

    }
);


/* ==================================================
   INITIALIZE
   ================================================== */

scrollToBottom();

chatInput.focus();