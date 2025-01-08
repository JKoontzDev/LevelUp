const daily_task_check = document.querySelectorAll('.check');
const username = document.querySelector('meta[name="username"]').content;
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const NumQuest = document.querySelector('meta[name="NumQuest"]').content;
const metaTag = document.querySelector('meta[name="NumQuest"]');
const questPanel = document.querySelector('.quests-panel');
const rewards = document.getElementById('rewards')
const percCom = document.getElementById('weeklyCom') //percentCompleted weekly
const tasks = document.querySelectorAll('.task');
const CharExp = document.querySelector('meta[name="exp"]').content;
const metaTagExp = document.querySelector('meta[name="exp"]');
const fillExp = document.getElementById('fillExp');
const messageBoard = document.getElementById('messages');
const questDetails = document.querySelectorAll('.questDetails');
const mainArea = document.querySelector('.main-content');
const progressOverview = document.querySelector('.progress-overview');


let num = 0;

daily_task_check.forEach((checkbox, index) => {
    checkbox.addEventListener('change', function () {
        if (this.checked) {
            setTimeout(() => {
                num += 1; // Increment the task counter
                alert(`Congrats! You have completed ${num} tasks!`);

                // Add the faded class to the corresponding task
                if (tasks[index]) {
                    tasks[index].classList.add('faded');
                }
                const spanElement = tasks[index].querySelector('span');

                const questName = spanElement.textContent;
                //console.log(questName);

                // Define the data to be sent in the fetch call
                const data = {
                    username: username,
                    taskIndex: questName,
                    NumQuest: NumQuest,
                    status: 'completed',
                    questName: questName
                };

                // Send a POST request
                fetch(`task/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify(data),
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok ' + response.statusText);
                        }
                        return response.json(); // Parse JSON response
                    })
                    .then(responseData => {
                        //add items to dashboard
                        fetch(`/dashboard/${username}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken,
                            },
                            body: JSON.stringify(responseData),
                        })
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Network response was not ok ' + response.statusText);
                                }
                                return response.json(); // Parse JSON response
                            })
                            .then(data => {
                                //console.log('Server Response2:', data);
                                metaTag.setAttribute('content', `${data.newNumQuest}`);  // Set new value to '10'
                                //console.log(metaTag);

                                if (metaTag.content == 0){
                                    const finished = `        <h3>Daily Quests</h3>
                                                <div class="task urgent">
                                                <span>All quests completed</span>
                                            </div>`;
                                    if (questPanel) {
                                        questPanel.innerHTML = finished;
                                    } else {
                                        console.error("Quest panel element not found");
                                    }
                                    }
                            })
                            //NumQuest.textContent = responseData
                        //console.log('Server Response:', responseData);
                        rewards.innerHTML = ''
                        for (let i = 0; i < responseData.drops.length; i++) {
                            const drop = responseData.drops[i]; // Get the current drop
                            const add_item_to_recieved = `<li>${drop}</li>`; // Use the drop value
                            rewards.innerHTML += add_item_to_recieved; // Append to the list
                        }
                        percCom.innerHTML = `${responseData.completed.toFixed(1)}%`; //percentage complete
                        //console.log(`${responseData.charExp} responseData.charExp`);
                        //console.log(`${CharExp} CharExp`);

                        if (responseData.charExp >= CharExp) {
                            metaTagExp.setAttribute('content', `${responseData.charExp}`); // Set new value to updated exp
                            let expWidth = `${responseData.charExp}`
                            fillExp.style.width = (expWidth) + '%';
                            //messageBoard.textContent = "You "
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            }, 200); // Delay of 200ms
        }
    });
});




// Bellow is used to get the quest details and display them in a <section>
const dataForQDetails = {
        message: 'Get quest details!',
        quests: [],
    }

questDetails.forEach((questDetails) => {
    dataForQDetails.quests.push(questDetails.textContent);
})

//console.log(dataForQDetails);
fetch(`/dashboard/${username}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(dataForQDetails),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json(); // Parse JSON response
    })
    .then(data => {
        //console.log(data);

        questDetails.forEach((questDetails) => {
            questDetails.addEventListener('click', function() {
                const questName = questDetails.textContent.trim();
                const Questjson = data.questDescription;
                let questDescription = '';


                Object.keys(Questjson).forEach(key => {
                    if (key === questName){
                        questDescription = Questjson[key];
                    }
                });



                const questDetailsAdded = document.getElementById('questDetailSec');
                if (questDetailsAdded) {
                    questDetailsAdded.querySelector('h3').textContent = questName;
                    questDetailsAdded.querySelector('p').textContent = questDescription;
                } else {
                    const sectionElement = document.createElement('section');
                    sectionElement.className = 'questDetailsSec';
                    sectionElement.id = 'questDetailSec'

                    const itemName = document.createElement('h3');
                    itemName.textContent = questName;
                    sectionElement.appendChild(itemName);

                    const itemDesc = document.createElement('p');
                    itemDesc.textContent = questDescription;
                    sectionElement.appendChild(itemDesc);

                    const Delete = document.createElement('button');
                    Delete.textContent = 'Delete';
                    Delete.className = "task urgent questDetailsDel"
                    sectionElement.appendChild(Delete);
                    Delete.addEventListener('click', function() {
                        sectionElement.remove();
                    })


                    mainArea.insertBefore(sectionElement, progressOverview);
                }

            })
        })

    })


// above is used to get the quest details and display them in a <section>



