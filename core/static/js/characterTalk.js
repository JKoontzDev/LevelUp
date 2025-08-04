document.addEventListener("DOMContentLoaded", () => {
  const chatWindow = document.getElementById("chat-window");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const username = document.querySelector('meta[name="username"]').content;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const journalBtn = document.getElementById("journal-btn");
  const journalOverlay = document.getElementById("journal-overlay");
  const closeJournal = document.getElementById("close-journal");
  const saveJournal = document.getElementById("save-journal");
  const fidget = document.getElementById("fidget-spinner");
  const url = `/dashboard/${username}/npc`;

  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  //journalBtn.addEventListener("click", () => {
  //  journalOverlay.style.display = "flex";
  //});

 // closeJournal.addEventListener("click", () => {
  //  journalOverlay.style.display = "none";
 // });

  //saveJournal.addEventListener("click", () => {
  //  alert("Journal saved! (Hook this to backend later.)");
 //   journalOverlay.style.display = "none";
  //});

  function sendMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    addMessage(text, "user");
    userInput.value = "";

    const typingBubble = document.createElement("div");
    typingBubble.className = "chat-message ai-message";

    const dots = document.createElement("div");
    dots.className = "typing-indicator";
    dots.innerHTML = `
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    `;
    typingBubble.appendChild(dots);

    chatWindow.appendChild(typingBubble);



    let data = {"text": text}
      fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Custom-User': username,
                'X-Custom-Name': "ME",
                'X-Custom-Message': text,

            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json(); // Parse JSON response
        })
        .then(responseData => {
            typingBubble.remove();
            console.log(responseData)
            addMessage(responseData.response, 'bot')

        })
  }

  function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = `chat-message ${sender}-message`;
    div.textContent = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }


  // Animate stars background
  const stars = document.getElementById("stars");

for (let i = 0; i < 100; i++) {
  const star = document.createElement("div");
  star.style.position = "absolute";
  star.style.width = "4px";
  star.style.height = "4px";
  star.style.background = "#fff";
  star.style.borderRadius = "50%";
  star.style.top = Math.random() * window.innerHeight + "px";
  star.style.left = Math.random() * window.innerWidth + "px";
  star.style.opacity = Math.random();

  const duration = 3 + Math.random() * 5; // 3–8s
  const delay = Math.random() * 5;

  star.style.animation = `float ${duration}s ease-in-out ${delay}s infinite alternate`;

  stars.appendChild(star);
}


  let isDragging = false;
  let angle = 0;
  let lastX = 0;


});
