const TUTORIAL_TOTAL_VIEWS = 5;

document.addEventListener("DOMContentLoaded", function () {
    const tutorial = document.querySelector('meta[name="tutorial"]').content.toLowerCase();
    if (tutorial === "true") return;


     const page = document.querySelector("[data-page]")?.dataset.page;


    const tutorialStepsByPage = {
        dashboard: [
            { target: "#tutorial-message", message: "Click this box to continue tutorial" },
            { target: "#quest-button", message: "View your daily tasks here." },
            { target: "#progress-overview", message: "Here’s your progress for completing daily tasks this week. Below, you can also find your recently added inventory items." },
            { target: "#motivation-bar", message: "This bar shows your characters health, and daily motivation. Use it wisely!" },
            { target: "#town-map-button", message: "Click here to begin your adventure, explore towns, and discover key locations like the market and blacksmith." },
            { target: "#message-board", message: "This is where any messages come through." },
            { target: "#settings", message: "This is where you can change user setting such as the daily number of quests or your user profile picture." },
            { target: "#settings", message: "Note, if you change your daily number of quests it will take affect at the next reset period." },
            { target: "#character", message: "Click here to see your characters inventory." },
            { target: "#tutorial-message", message: "Welcome to Level Up!" },

        ],
        character: [
            { target: "#stats-panel", message: "These are your current character stats. Train to improve them." },
            { target: "#redo-tutorial", message: "Click here to redo the tutorial anytime." },
        ],
        trainingGrounds: [
            { target: "#character-stats", message: "This section is where you can train with magic or any weapon." },
            { target: "#character-stats", message: "There are two ways to train. Safe or Intense, be mindful that if you train intensely and fail you may hurt yourself." },
            { target: "#character-skills", message: "When you unlock certain skills they will appear here. They can be trained similar to your magic and weapons." },
            { target: "#tutorial-message", message: "Train daily to get stronger, discipline is key." },
        ],
        blacksmith: [
            { target: "#tutorial-message", message: "This is the blacksmith. Here you can forge new gear, repair and upgrade existing gear, and smelt your collected ore." },

        ],
        market: [
            { target: "#tutorial-message", message: "This is the market. Here you can buy different items for your journey or hobbies." },
        ],
        guildHall: [
            { target: "#tutorial-message", message: "This is the Ironstead guild hall. Here you can participate in quests and interact with your fellow guild mates." },
            { target: "#quest-board", message: "Like how you have your own personal real life quests, you can send your character on guests too." },
            { target: "#quest-board", message: "Each quest takes a certain amount of time to complete." },
            { target: "#quest-board", message: "Some quests are dangerous so make sure your character is prepared." },
            { target: "#guildMaster", message: "Here you can interact with the guild master." },
            { target: "#masterChat", message: "Feel free to talk to the guild master, I hear she's really nice!" },
            { target: "#rewardsButton", message: "When your character completes a quest you can get your reward here." },
            { target: "#bulletin", message: "Here is the bulletin board. On it will be descriptions for the available quests." },
            { target: "#members", message: "You're not here alone, I wonder if anyone has anything interesting to say?" },
        ],
    };

    const steps = tutorialStepsByPage[page] || [];
    if (steps.length === 0) return;

    let currentStep = 0;
    let overlay, messageBox;

    function createTutorialUI() {
        overlay = document.createElement("div");
        overlay.id = "tutorial-overlay";
        overlay.style = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.2);
            z-index: 9998;
        `;
        document.body.appendChild(overlay);

        messageBox = document.createElement("div");
        messageBox.id = "tutorial-message";
        messageBox.style = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #fff;
            padding: 1rem;
            border-radius: 12px;
            z-index: 9999;
            max-width: 90%;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
            cursor: pointer;
            color: black;
        `;
        document.body.appendChild(messageBox);

        messageBox.addEventListener("click", nextStep);
    }

    function highlightElement(step) {
    const element = document.querySelector(step.target);
    if (!element) {
        console.warn(`Tutorial: Element not found: ${step.target}`);
        currentStep++;
        if (currentStep >= steps.length) {
            document.body.removeChild(overlay);
            document.body.removeChild(messageBox);
            console.log(page);
            markViewAsCompleted(page);
        } else {
            highlightElement(steps[currentStep]);
        }
        return;
    }

    element.scrollIntoView({ behavior: "smooth", block: "center" });
    element.style.boxShadow = "0 0 10px 4px yellow";
    console.log(messageBox);
    console.log(step.message);
    messageBox.innerText = step.message;
    }

    function clearHighlight() {
        const previous = document.querySelector(steps[currentStep - 1]?.target);
        if (previous) {
            previous.style.boxShadow = "none";
        }
    }

    function nextStep() {
        clearHighlight();
        if (currentStep >= steps.length) {
            document.body.removeChild(overlay);
            document.body.removeChild(messageBox);
            markViewAsCompleted(page);
            return;
        }

        highlightElement(steps[currentStep]);
        currentStep++;
    }


    function markViewAsCompleted(viewName) {
        let completedCount = parseInt(localStorage.getItem("tutorial_completed") || "0");

        const viewed = JSON.parse(localStorage.getItem("tutorial_views") || "[]");

        if (!viewed.includes(viewName)) {
            viewed.push(viewName);
            localStorage.setItem("tutorial_views", JSON.stringify(viewed));

            completedCount += 1;
            localStorage.setItem("tutorial_completed", completedCount);
        }

        if (completedCount >= TUTORIAL_TOTAL_VIEWS) {
            completeTutorial(); // this is where you call the fetch
        }
    }


    function completeTutorial() {
        alert("You completed the tutorial! Feel free to reactivate it in the settings if you need a refresher. Enjoy Level Up!")
        fetch("/api/complete_tutorial/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(), // your CSRF handling here
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ tutorial_complete: true }),
        }).then(res => {
            if (res.ok) {
                console.log("Tutorial completion saved.");
                localStorage.removeItem("tutorial_completed");
                localStorage.removeItem("tutorial_views");
            }
        });
    }

    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.content || "";
    }

    // Start the tutorial
    createTutorialUI();
    nextStep();
});
