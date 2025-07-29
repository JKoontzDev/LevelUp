const buttons = document.querySelectorAll('.actionButton');
const tabs = document.querySelectorAll('.tab');
const questList = document.getElementById('questList');
const username = document.querySelector('meta[name="username"]').content;
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const url = `/dashboard/${username}/ironstead/guild/hall/api`;
const npc = `/dashboard/${username}/npc`;
const masterText = document.getElementById('masterText');
//action tabs
const talkTab = document.getElementById('talk');
const rewardsTab = document.getElementById('rewards');
const memberChatButton = document.getElementById('memberChat');
const npcButtons = document.querySelectorAll(".NPCButton");
const rewardsButton = document.getElementById("rewardsButton");

let questGoldValue;

// quest tabs
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelector('.tab.active').classList.remove('active');
    tab.classList.add('active');
    filterQuests(tab.getAttribute('data-type'));
  });
});


//guild master buttons
document.querySelectorAll(".GMButton").forEach(button => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".GMButton").forEach(btn => btn.classList.remove("active"));
            document.querySelectorAll(".actionArea").forEach(area => area.classList.remove("active"));
            button.classList.add("active");
            const targetId = button.getAttribute("data-target");
            document.getElementById(targetId).classList.add("active");
        });
    });


//quest names
function filterQuests(type) {
  const quests = questList.querySelectorAll('li');
  quests.forEach(quest => {
    quest.style.display = quest.getAttribute('data-type') === type ? 'flex' : 'none';
  });
}



let currentNPC = null;

npcButtons.forEach(button => {
    button.addEventListener("click", (event) => {
        const chatArea = document.getElementById('chatArea');
        const npcId = event.target.id;
        while (chatArea.firstChild) {
            chatArea.removeChild(chatArea.firstChild);
        }
        //console.log("NPC clicked:", npcId);
        currentNPC = npcId;
        const newMessage = document.createElement('p');
        newMessage.innerHTML = `<strong>${npcId}:</strong> Hello Traveller`;
        chatArea.appendChild(newMessage);
        //console.log(currentNPC);
    });
});


// member chat

memberChatButton.addEventListener("click", () => {
    //console.log(currentNPC);
    if (!currentNPC) return;
    const memberChatText = document.getElementById('memberChatText').value;
    //console.log(memberChatText);
    document.getElementById('memberChatText').value = '';
    const chatArea = document.getElementById('chatArea');
    const newMessage = document.createElement('p');
    newMessage.innerHTML = `<strong>You:</strong> ${memberChatText}`;
    chatArea.appendChild(newMessage);
    fetch(npc, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Custom-User': username,
                'X-Custom-Message': memberChatText,
                'X-Custom-Name': currentNPC,
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json(); // Parse JSON response
            })
            .then(responseData => {
                //console.log(responseData);
                const chatArea = document.getElementById('chatArea');
                const newMessage = document.createElement('p');
                newMessage.innerHTML = `<strong>${currentNPC}:</strong> ${responseData.response}`;
                chatArea.appendChild(newMessage);
            })
})



function getMasterText() {
//guild master talk
    fetch(npc, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Custom-User': username,
                    'X-Custom-Message': "Hello Guild Master",
                    'X-Custom-Name': "Amanda Thornwood",


                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json(); // Parse JSON response
            })
            .then(responseData => {
                //console.log(responseData);
                masterText.textContent = responseData.response;
            })
}



function sanitizeInput(input) {
    const dangerousChars = /[<>;{}()[\]`]/g;
    return input.replace(dangerousChars, "");
}


function talkToMaster(message) {

   fetch(npc, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Custom-User': username,
                    'X-Custom-Message': message,
                    'X-Custom-Name': "Amanda Thornwood",
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json(); // Parse JSON response
            })
            .then(responseData => {
                //console.log(responseData);
                masterText.textContent = responseData.response;
            })
}

document.getElementById("sendButton").addEventListener("click", async () => {
        const playerInput = document.getElementById("messageInput").value.trim();
        if (!playerInput) {
            alert("Please enter a message!");
            return;
        }
        // Set a loading state
        document.getElementById("masterText").textContent = "Amanda is thinking...";
        const message = sanitizeInput(playerInput);
        talkToMaster(message)
})


buttons.forEach(button => {
    button.addEventListener('click', (e) => {
        let questName = e.target.id
        alert(`Starting quest: ${questName}`);
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Custom-User': username,
                'X-Custom-Message': questName,


            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json(); // Parse JSON response
        })
        .then(responseData => {
            //console.log(responseData);
        })
    })
})




function getReward(item) {
    fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Custom-User': username,
                'X-Custom-Message': "getReward",
            },
            body: JSON.stringify(item),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json(); // Parse JSON response
        })
        .then(responseData => {
           console.log(responseData);
           masterText.textContent = `Here is your ${item}, and your ${responseData.gold} gold, thank you!`;
           rewardsTab.textContent = 'No rewards to redeem';
           const btn = document.getElementById(item);
           const li = btn?.closest("li");
           if (li) li.remove();

        })



}




rewardsButton.addEventListener("click", () => {
    fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Custom-User': username,
                'X-Custom-Message': "rewards",
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json(); // Parse JSON response
        })
        .then(responseData => {
            //console.log(responseData);
            items = responseData.reward;
            //console.log(items);
            if (typeof items == 'undefined') {
                rewardsTab.textContent = 'No rewards to redeem';
                masterText.textContent = `Once you finish a quest, your reward will be here.`;

            } else {
                questGoldValue = responseData.gold;
                masterText.textContent = `Welcome back! I see you finished ${responseData.questName}. Which reward would you like?`;
                items.forEach(item => {
                    const rewardContainer = document.createElement('div');
                    rewardContainer.classList.add('reward-item');

                    const itemLabel = document.createElement('div');
                    itemLabel.textContent = item.name;

                    const button = document.createElement('button');
                    button.textContent = `Choose ${item}`;
                    button.id = item;
                    button.classList.add('NPCButton');


                    rewardContainer.appendChild(itemLabel);
                    rewardContainer.appendChild(button);
                    rewardsTab.appendChild(rewardContainer);

                    button.addEventListener('click', function (){
                        getReward(button.id);
                    })
                })
            }
        })
});





getMasterText()
filterQuests(document.querySelector('.tab.active').getAttribute('data-type'));
