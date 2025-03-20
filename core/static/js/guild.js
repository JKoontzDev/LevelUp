

// Tab functionality for filtering quests
const tabs = document.querySelectorAll('.tab');
const questList = document.getElementById('questList');

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelector('.tab.active').classList.remove('active');
    tab.classList.add('active');
    filterQuests(tab.getAttribute('data-type'));
  });
});

function filterQuests(type) {
  const quests = questList.querySelectorAll('li');
  quests.forEach(quest => {
    quest.style.display = quest.getAttribute('data-type') === type || type === 'other' ? 'flex' : 'none';
  });
}

function startQuest(questName) {
  alert(`Starting quest: ${questName}`);
  // Validate equipment, update player status, etc.
}

function openShop() {
  alert("Opening equipment workshop. Prepare your gear!");
  // Navigate to a detailed workshop view or open a modal window.
}

function handleChat(event) {
  if (event.key === "Enter" && event.target.value.trim() !== "") {
    const chatArea = document.getElementById('chatArea');
    const newMessage = document.createElement('p');
    newMessage.innerHTML = `<strong>You:</strong> ${event.target.value}`;
    chatArea.appendChild(newMessage);
    event.target.value = "";
    // In a full implementation, push this message to a backend or real-time service.
  }
}





filterQuests(document.querySelector('.tab.active').getAttribute('data-type'));
