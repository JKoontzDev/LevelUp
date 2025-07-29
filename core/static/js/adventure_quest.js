//MAIN START
const characterArea = document.getElementById('characterArea');
const mainContent = document.querySelector('.mainContent');
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const username = document.querySelector('meta[name="username"]').content;
const url = `/${username}/adventure/quest/api`;
let currentPlayerHealth = document.querySelector('meta[name="currentPlayerHealth"]').content;
let currentPlayerHealthBase = document.querySelector('meta[name="currentPlayerHealth"]');
const basePlayerHealth = document.querySelector('meta[name="basePlayerHealth"]').content;
const characterUI = document.getElementById('characterUI');

//global vars for story
//character
let character;
//dialogue lines pulled from backend
let dialogueLines = [];
//current index to get lines from dialogue lines
let currentLineIndex = 0;
//list of choices
let choices = [];
//checks if enemies are present in this scene and if so will start combat
let enemyScene = false;
let enemyList = [];

let combatEndCallback = null;



// fetch character details on load up
fetch(url, {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Custom-Message': 'character',
        'X-Custom-User': username
    },
})
.then(response => {
    if (!response.ok) {
        return response.text().then(text => {
            console.error('Non-OK response:', response.status, text);
            throw new Error('Network response was not ok');
        });
    }
    return response.json(); // Only if response is OK
})
.then(responseData => {
    character = responseData;
    //console.log(character);
})
.catch(error => {
    console.error('Fetch error:', error);
});




// used to pull info from backend
async function grabInfo(methodStatus, message, data) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Custom-Message': message,
        'X-Custom-User': username
    };

    const options = {
        method: methodStatus.toUpperCase(),
        headers: headers
    };

    if (methodStatus === "post") {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const responseData = await response.json();
        return responseData;
    } catch (error) {
        console.error("Fetch error:", error);
        throw error;
    }
}


// BELOW IS FIGHT< BELOW THE FIGHT IS THE STORY


// used to change the health and health bar 0==healing
async function healthFun(healthFor, amount, isHealing, targetName, index, enemyArray) {
    //0 is player, 1 is enemy
    //console.log(`Amount health ${amount}`);
    if (healthFor === 0) {
        let playerHealth = document.getElementById('playerHealth');
        const playerHealthBar = document.getElementById('playerHealthBar');
        const playerBaseHealth = playerHealth.dataset.number;
        // get new updated health
        let newHealth;
        if(isHealing === 0) {
            newHealth = (Number(currentPlayerHealth) + Number(amount));
        } else {
            newHealth = (currentPlayerHealth - amount);
        }
        // send message of ammount taken or healed
        if (newHealth > currentPlayerHealth) {
            addMessage(0, `You healed yourself by ${amount}, you feel more energized!`, targetName = 'player', index = 0)
        } else if (newHealth < 0) {
            addMessage(0, `${username} took fatal damage! ${username} has died`, 'player', 0)
            deadMode(username)
        } else {
            addMessage(0, `${targetName} took ${amount} damage!`, targetName, index)

        }

        currentPlayerHealth = newHealth;
        //make a percentage
        let newHealthPercentage = (newHealth / playerBaseHealth) * 100;
        //update the UI
        playerHealth.textContent = `${newHealth} / ${basePlayerHealth}`;
        playerHealthBar.style.width = `${newHealthPercentage}%`

    }
    else {
        // get new updated enemy health
        // get the characters id
        const healthId = `health-${targetName.toLowerCase()}-${index}`;
        //console.log(`healthID = ${healthId}`);
        const healthBarId = `healthBar-${targetName.toLowerCase()}-${index}`;
        // get span
        const healthSpan = document.getElementById(healthId);
        const healthBarSpan = document.getElementById(healthBarId);

        // current health
        let enemyCurrentHealth = healthSpan.dataset.number;
        const enemyBaseNumber = healthSpan.dataset.baseNumber;
        let newHealth;
        if(isHealing === 0) {
            newHealth = (Number(enemyCurrentHealth) + Number(amount));
        } else {
            newHealth = (enemyCurrentHealth - amount);
        }
        //console.log(targetName);
        //console.log(index)
        if (newHealth > enemyCurrentHealth) {
            addMessage(1, `${targetName} healed themselves by ${amount}, they feel more energized!`, targetName, index)

        } else if (newHealth <= 0) {
            addMessage(1, `${targetName} took fatal damage! ${targetName} has died`, targetName, index)
            const div = `div-${targetName.toLowerCase()}-${index}`
            removeEnemyBox(div, targetName, enemyArray)
        } else {
            addMessage(1, `${targetName} took ${amount} damage!`, targetName, index)

        }
        // make the base and current health new health
        healthSpan.dataset.number = newHealth;
        //make a percentage
        let newHealthPercentage = (newHealth / enemyBaseNumber) * 100;
        //update the UI
        //console.log(`newHealthPercentage = ${newHealthPercentage}`);
        healthSpan.textContent = `${newHealth} / ${enemyBaseNumber}`;
        if(newHealthPercentage < 0) {
            healthBarSpan.style.width = `0%`
        } else {
            healthBarSpan.style.width = `${newHealthPercentage}%`

        }


    }

}



// ADD MESSAGE
async function addMessage(messageFor, message, targetName='', index) {
    const playerMessage = document.getElementById('playerMessage');
    if (messageFor === 0) {
        // Message is for the player
        if (playerMessage) {
            playerMessage.textContent = message;
        }
    } else if (messageFor === 1) {
        // Message is for a specific enemy
        const id = `message-${targetName.toLowerCase()}-${index}`;
        const enemyMessage = document.getElementById(id);
        if (enemyMessage) {
            enemyMessage.textContent = message;
        } else {
            console.warn(`No enemy message box found for id: ${id}`);
        }
    }
}


// WILL ADD CHARACTER TO SCREEN
async function createCharacterElement(url, characters) {
  characterArea.textContent = '';
  characters.forEach((character, index) => {
      //console.log(`CreateIMG: ${character}`);
      if(character === "Enemy") {
        return;
      }
      else {
          // make div
          const container = document.createElement('div');
          container.classList.add('characterContainer');
          // add img
          const sprite = document.createElement('img');
          sprite.classList.add('characterSprite');
          sprite.setAttribute('src', url[index]);
          sprite.setAttribute('alt', character);
          container.appendChild(sprite);
          // add message div
          const messageDiv = document.createElement('div');
          messageDiv.classList.add('characterMessage');
          messageDiv.setAttribute('id', `message-${character}`);  // Give each message div an ID based on the character name

          // append
          container.appendChild(messageDiv);
          characterArea.appendChild(container);

      }
    });
}



// WILL ADD ENEMY HEALTH UI TO SCREEN
// enemyHealth = [], enemyName = [], numberOfEnemies=INT
//start of comabt
async function createEnemyBox(enemyHealth, enemyName, numberOfEnemies) {
  for (let i = 0; i < numberOfEnemies; i++) {
      const columnDiv = document.createElement('div');
      columnDiv.classList.add('column');
      columnDiv.id = `div-${enemyName[i].toLowerCase()}-${i}`

      const uiBox = document.createElement('div');
      uiBox.classList.add('uiBox');
      uiBox.dataset.name = enemyName[i];
      //uiBox.dataset.skillActive = '';

      const h2 = document.createElement('h2');
      h2.textContent = `${enemyName[i]}`;

      const healthStat = document.createElement('div');
      healthStat.classList.add('health-stat');
      //healthStat.dataset.number = `${enemyHealth[i]}`
      const skullSpan = document.createElement('span');
      skullSpan.textContent = String.fromCodePoint(0x2622);
      const healthSpan = document.createElement('span');
      healthSpan.dataset.number = `${enemyHealth[i]}`
      healthSpan.dataset.baseNumber = `${enemyHealth[i]}`

      healthSpan.id = `health-${enemyName[i].toLowerCase()}-${i}`;
      healthSpan.textContent = ` ${enemyHealth[i]} / ${enemyHealth[i]}`;
      healthStat.appendChild(skullSpan);
      healthStat.appendChild(healthSpan);

      const healthBar = document.createElement('div');
      healthBar.classList.add('health-bar');
      const healthBarInner = document.createElement('div');
      healthBarInner.classList.add('health-bar-inner');
      healthBarInner.id = `healthBar-${enemyName[i].toLowerCase()}-${i}`;
      healthBarInner.style.width = `100%`;
      healthBar.appendChild(healthBarInner);

      uiBox.appendChild(h2);
      uiBox.appendChild(healthStat);
      uiBox.appendChild(healthBar);



      const messageContainer = document.createElement('div');
      messageContainer.classList.add('message-container');
      const messageP = document.createElement('p');
      messageP.classList.add('message');
      messageP.id = `message-${enemyName[i].toLowerCase()}-${i}`;
      messageP.textContent = 'No new notifications';
      messageContainer.appendChild(messageP);

      columnDiv.appendChild(uiBox);
      columnDiv.appendChild(messageContainer);

      characterUI.appendChild(columnDiv);
  }
  battleMode(enemyName)
}


//REMOVE ENEMY BOX AFTER DEATH
async function removeEnemyBox(target, name, enemies) {
    //console.log(name);
    let div = document.getElementById(target);
    setTimeout(() => {
          div.remove();
    }, 2000);

    newEnemies = enemies.filter(item => item !== name);
    if (newEnemies.length === 0) {
        alert("You killed all enemies");
        stopCombat();
    }
    //console.log(`ENEMY REMOVED: ${newEnemies}`);
    combatControls(newEnemies);


}



// Will add combat controls
async function combatControls(enemies) {
    //console.log(`THIS IS A TEST: ${enemies}`);

    const controls = document.getElementById('controls');
    controls.textContent = '';
    const attackButton = document.createElement('button');
    attackButton.id = 'attBtn';
    attackButton.textContent = "Attack";
    attackButton.classList.add("combatButton");
    attackButton.addEventListener('click', () => {
        attackControl(enemies);
    })
    const blockButton = document.createElement('button');
    blockButton.id = 'bloBtn';
    blockButton.textContent = "Block";
    blockButton.classList.add("combatButton");
    blockButton.addEventListener('click', () => {
        finishRound(true, enemies);
    })

    const magicButton = document.createElement('button');
    magicButton.id = 'magBtn';
    magicButton.textContent = "Magic";
    magicButton.classList.add("combatButton");
    magicButton.addEventListener('click', () => {
        magicControl(enemies);
    })

    const skillsButton = document.createElement('button');
    skillsButton.id = 'skillsBtn';
    skillsButton.textContent = "Skills";
    skillsButton.classList.add("combatButton");
    skillsButton.addEventListener('click', () => {
        skillsControl(enemies);
    })


    const finishRoundButton = document.createElement('button');
    finishRoundButton.id = 'frBtn';
    finishRoundButton.textContent = "Finish Round";
    finishRoundButton.classList.add("combatButton");
    finishRoundButton.addEventListener('click', () => {

        finishRound(false, enemies);
    })

    controls.appendChild(attackButton);
    controls.appendChild(blockButton);
    controls.appendChild(magicButton);
    controls.appendChild(skillsButton);
    controls.appendChild(finishRoundButton);

}



// Used to show character stats and skills
async function getCharacterMenu(characterData) {
    console.log(characterData);
    const uiContent = [
        //0      1        if {} 0-len
      ['Rank', characterData.characterRank || 'Unknown Rank'],
      ['Magic', characterData.characterMagic || 'No Magic'],
      ['Armor', characterData.characterArmor || 'No Armor'],
      ['Weapons', characterData.characterWeapon || 'No Weapon'],
      ['Skills', characterData.characterSkills|| ['No Skills']],
      ['Pets', 'None'] // Update this when pet data is available
    ];
    console.log(uiContent);

    let playerStats = document.getElementById('playerStats');
    if (!playerStats) {
        playerStats = document.createElement('div');
        playerStats.className = 'characterUI';
        playerStats.id = 'playerStats';
        document.body.appendChild(playerStats);
    } else {
        playerStats.textContent = '';
    }

    for (let i = 0; i < uiContent.length; i++) {
        const column = document.createElement('div');
        column.className = 'column';

        const uiBox = document.createElement('div');
        uiBox.className = 'uiBoxStats';

        const head = document.createElement('h2');
        head.textContent = uiContent[i][0];
        uiBox.appendChild(head);
        const value = uiContent[i][1];
        const type =  uiContent[i][0];
        //console.log(`Value is ${type}`);

        if (type === "Rank") {
            const body = document.createElement('p');
            body.textContent = value.name;
            body.addEventListener('click', () => {alert("Rank: " + value.name + "\n\nDamage: " + value.damage  + "\n\nDescription: " + value.description);})

            uiBox.appendChild(body);
        } else if (type === "Magic") {
            if (Array.isArray(value)) {
                // If it's an array, create a <p> for each item
                value.forEach(val => {
                    const item = document.createElement('p');
                    item.textContent = val.name;
                    uiBox.appendChild(item);
                    item.addEventListener('click', () => {alert("Magic: " + val.name + "\n\nDamage: " + val.damage
             + "\n\nHealing: " + val.healing + "\n\nDamage Modifier : " + val.damageModifier + "\n\nHealing Modifier : " + val.healingModifier + "\n\nDexterity : " + val.dexterity + "\n\nDescription: " + val.description);})
                });
           }
        } else if (type === "Armor") {
            if (Array.isArray(value)) {
                value.forEach(val => {
                    const item = document.createElement('p');
                    item.textContent = val.name;
                    uiBox.appendChild(item);
                    item.addEventListener('click', () => {alert("Armor: " + val.name + "\n\nDefense: " + val.defense
             + "\n\nEfficiency: " + val.efficiency + "\n\nDefense Modifier : " + val.defenseModifier + "\n\nDexterity : " + val.dexterity + "\n\nDescription: " + val.description);})
                });
           }

        } else if (type === "Weapons") {
            if (Array.isArray(value)) {
                value.forEach(val => {
                    const item = document.createElement('p');
                    item.textContent = val.name;
                    uiBox.appendChild(item);
                    item.addEventListener('click', () => {alert("Weapon: " + val.name + "\n\nDamage: " + val.damage +
                    "\n\nDamage Modifier: " + val.damageModifier + "\n\nEfficiency: " + val.efficiency + "\n\nDescription: " + val.description );})
                });
           }
        } else if (type === "Skills") {
            if (Array.isArray(value)) {
                value.forEach(val => {
                    const item = document.createElement('p');
                    item.textContent = val.name;
                    uiBox.appendChild(item);
                    item.addEventListener('click', () => {alert("Skill: " + val.name + "\n\nDamage: " + val.damage
                    + "\n\nDamage Modifier: " + val.damage_modifier + "\n\nHealing: " + val.healing + "\n\nHealing Modifier: " + val.healing_modifier
                     + "\n\nDexterity : " + val.dexterity + "\n\nDescription: " + val.description );})
                });
            }
        } else if (type === "Pets") {
            const body = document.createElement('p');
            body.textContent = value.name;
            //body.addEventListener('click', () => {alert("Weapon: " + value.name + "\n\nDamage: " + value.damage + "\n\nDescription: " + value.description);})

            uiBox.appendChild(body);
        }

        column.appendChild(uiBox);
        playerStats.appendChild(column);
    }
}




// marks the enemy as active for use in fighting
async function clickActive(uiBox) {
    uiBox.forEach(div => {
        div.addEventListener('click', () => {
            uiBox.forEach(box => box.classList.remove('active')); // remove from all
            div.classList.add('active'); // add to the clicked one
            let divSelect = document.querySelector('.active');
            let selected = divSelect.dataset.name;
            if (selected == username){
                playerStats.classList.toggle('hidden')
                getCharacterMenu(character);
            }
        });
    });
}





// combat for physical attacks
async function attackControl(enemies) {
    const uiContent = [
        //0      1        if {} 0-len
      ['Rank', character.characterRank || 'Unknown Rank'],
      ['Magic', character.characterMagic || 'No Magic'],
      ['Armor', character.characterArmor || 'No Armor'],
      ['Weapons', character.characterWeapon || 'No Weapon'],
      ['Skills', character.characterSkills|| ['No Skills']],
      ['Pets', 'None'] // Update this when pet data is available
    ];
    const rankAttack = uiContent[0][1];
    const weapons = uiContent[3][1];
    const skills = uiContent[4][1];



    const controls = document.getElementById('controls');
    controls.textContent = '';
    const rankSkillButton = document.createElement('button');
    rankSkillButton.id = 'rankSkillBtn';
    rankSkillButton.textContent = `${rankAttack.attack}`;
    rankSkillButton.classList.add("combatButton");
    rankSkillButton.addEventListener('click', () => {
        //get target
        let target = document.querySelector('.active');
        //if no target send alert
        if (!target) {
            alert('No active target selected.');
            return;
        }
        //remove all other targets
        document.querySelectorAll('.uiBox').forEach(box => {
            if (box !== target) {
                box.removeAttribute('data-attack-active');
            }
        });
        //add target
        target.dataset.attackActive = `${rankAttack.attack}`;
        //get enemy name / display message to players message
        const enemyName =  target.getAttribute('data-name');
        addMessage(0, `You have targeted ${enemyName} with ${rankAttack.attack}`)
    })
    controls.appendChild(rankSkillButton);


    if (Array.isArray(weapons)){
        weapons.forEach(item => {
            const weaponAttackButton = document.createElement('button');
            weaponAttackButton.id = 'weaponAttackBtn';
            weaponAttackButton.textContent = `Attack With ${item.name}`;
            weaponAttackButton.classList.add("combatButton");
            controls.appendChild(weaponAttackButton);
            weaponAttackButton.addEventListener('click', () =>{
                //get target
                let target = document.querySelector('.active');
                //if no target send alert
                if (!target) {
                    alert('No active target selected.');
                    return;
                }
                //remove all other targets
                document.querySelectorAll('.uiBox').forEach(box => {
                    if (box !== target) {
                        box.removeAttribute('data-attack-active');
                    }
                });
                //add target
                //get enemy name / display message to players message
                const enemyName =  target.getAttribute('data-name');
                addMessage(0, `You have targeted ${enemyName} with ${item.name}`)
                target.dataset.attackActive = `${item.name}`;
            })
        })

    } else {
        const weaponAttackButton = document.createElement('button');
        weaponAttackButton.id = 'weaponAttackBtn';
        weaponAttackButton.textContent = `Attack With ${weapons.name}`;
        weaponAttackButton.classList.add("combatButton");
        controls.appendChild(weaponAttackButton);
        weaponAttackButton.addEventListener('click', () => {
            //get target
            let target = document.querySelector('.active');
            //if no target send alert
            if (!target) {
                alert('No active target selected.');
                return;
            }
            //remove all other targets
            document.querySelectorAll('.uiBox').forEach(box => {
                if (box !== target) {
                    box.removeAttribute('data-attack-active');
                }
            });
            //get enemy name / display message to players message
            const enemyName =  target.getAttribute('data-name');
            addMessage(0, `You have targeted ${enemyName} with ${weapons.name}`)

            target.dataset.attackActive = `${weapons.name}`;

        })

    }
    //back button
    const backButton = document.createElement('button');
    backButton.id = 'backBtn';
    backButton.textContent = "Go Back";
    backButton.classList.add("combatButton");
    controls.appendChild(backButton);
    backButton.addEventListener('click', () => {
        combatControls(enemies);
    })
}


// combat for magic attacks
async function magicControl(enemies) {
    const uiContent = [
        //0      1        if {} 0-len
      ['Rank', character.characterRank || 'Unknown Rank'],
      ['Magic', character.characterMagic || 'No Magic'],
      ['Armor', character.characterArmor || 'No Armor'],
      ['Weapons', character.characterWeapon || 'No Weapon'],
      ['Skills', character.characterSkills|| ['No Skills']],
      ['Pets', 'None'] // Update this when pet data is available
    ];
    const rankAttack = uiContent[0][1];
    const magic = uiContent[1][1];


    const controls = document.getElementById('controls');
    controls.textContent = '';
    const rankSkillButton = document.createElement('button');
    rankSkillButton.id = 'rankSkillBtn';
    rankSkillButton.textContent = `${rankAttack.attack}`;
    rankSkillButton.classList.add("combatButton");
    rankSkillButton.addEventListener('click', () => {
        //get target
        let target = document.querySelector('.active');
        //if no target send alert
        if (!target) {
            alert('No active target selected.');
            return;
        }
        //remove all other targets
        document.querySelectorAll('.uiBox').forEach(box => {
              if (box !== target) {
              box.removeAttribute('data-attack-active');
              }
        });
        //add target
        target.dataset.attackActive = `${rankAttack.attack}`;
        //get enemy name / display message to players message
        const enemyName =  target.getAttribute('data-name');
        addMessage(0, `You have targeted ${enemyName} with ${rankAttack.attack}`)

        })

    controls.appendChild(rankSkillButton);


    if (Array.isArray(magic)){
        magic.forEach(item => {
            const magicAttackButton = document.createElement('button');
            magicAttackButton.id = 'magicAttackBtn';
            magicAttackButton.textContent = `Attack With ${item.name}`;
            magicAttackButton.classList.add("combatButton");
            controls.appendChild(magicAttackButton);
            magicAttackButton.addEventListener('click', () => {
                //get target
                let target = document.querySelector('.active');
                //if no target send alert
                if (!target) {
                    alert('No active target selected.');
                    return;
                }
                //remove all other targets
                document.querySelectorAll('.uiBox').forEach(box => {
                      if (box !== target) {
                      box.removeAttribute('data-attack-active');
                      }
                });
                //add target
                target.dataset.attackActive = `${item.name}`;
                //get enemy name / display message to players message
                const enemyName =  target.getAttribute('data-name');
                addMessage(0, `You have targeted ${enemyName} with ${item.name}`)
            })
        })

    } else {
        const magicAttackButton = document.createElement('button');
        magicAttackButton.id = 'magicAttackBtn';
        magicAttackButton.textContent = `Attack With ${magic.name}`;
        magicAttackButton.classList.add("combatButton");
        controls.appendChild(magicAttackButton);
        magicAttackButton.addEventListener('click', () => {
            //get target
            let target = document.querySelector('.active');
            //if no target send alert
            if (!target) {
               alert('No active target selected.');
               return;
            }
            //remove all other targets
            document.querySelectorAll('.uiBox').forEach(box => {
                 if (box !== target) {
                 box.removeAttribute('data-attack-active');
                 }
            });
            //add target
            target.dataset.attackActive = `${magic.name}`;
            //get enemy name / display message to players message
            const enemyName =  target.getAttribute('data-name');
            addMessage(0, `You have targeted ${enemyName} with ${magic.name}`)

        })
    }

    //back button
    const backButton = document.createElement('button');
    backButton.id = 'backBtn';
    backButton.textContent = "Go Back";
    backButton.classList.add("combatButton");
    controls.appendChild(backButton);
    backButton.addEventListener('click', () => {
        combatControls(enemies);
    })

}


// skills for physical/magic attacks
async function skillsControl(enemies) {
    const uiContent = [
        //0      1        if {} 0-len
      ['Rank', character.characterRank || 'Unknown Rank'],
      ['Magic', character.characterMagic || 'No Magic'],
      ['Armor', character.characterArmor || 'No Armor'],
      ['Weapons', character.characterWeapon || 'No Weapon'],
      ['Skills', character.characterSkills|| ['No Skills']],
      ['Pets', 'None'] // Update this when pet data is available
    ];

    const controls = document.getElementById('controls');
    controls.textContent = '';


    const rankAttack = uiContent[0][1];
    const skills = uiContent[4][1];

    const rankSkillButton = document.createElement('button');
    rankSkillButton.id = 'rankSkillBtn';
    rankSkillButton.textContent = `${rankAttack.attack}`;
    rankSkillButton.classList.add("combatButton");
    rankSkillButton.addEventListener('click', () => {
        //get target
        let target = document.querySelector('.active');
        //if no target send alert
        if (!target) {
            alert('No active target selected.');
            return;
        }
        //remove all other targets
        document.querySelectorAll('.uiBox').forEach(box => {
              if (box !== target) {
              box.removeAttribute('data-attack-active');
              }
        });
        //add target
        target.dataset.attackActive = `${rankAttack.attack}`;
        //get enemy name / display message to players message
        const enemyName =  target.getAttribute('data-name');
        addMessage(0, `You have targeted ${enemyName} with ${rankAttack.attack}`)
    })

    controls.appendChild(rankSkillButton);




    if (Array.isArray(skills)){
        skills.forEach(item => {
            const skillsButton = document.createElement('button');
            skillsButton.id = 'skillsBtn';
            skillsButton.textContent = `Use skill ${item.name}`;
            skillsButton.classList.add("combatButton");
            controls.appendChild(skillsButton);
            skillsButton.addEventListener('click', () => {
                //get target
                let target = document.querySelector('.active');
                //if no target send alert
                if (!target) {
                    alert('No active target selected.');
                    return;
                }
                //remove all other targets
                document.querySelectorAll('.uiBox').forEach(box => {
                    if (box !== target) {
                      box.removeAttribute('data-skill-active');
                    }
                  });
                //add target
                target.dataset.skillActive = `${item.name}`;
                //get enemy name / display message to players message
                const enemyName =  target.getAttribute('data-name');
                addMessage(0, `You have targeted ${enemyName} with ${item.name}`)
            })
        })
    } else {
        const skillsButton = document.createElement('button');
        skillsButton.id = 'skillsBtn';
        skillsButton.textContent = `Use skill ${skills.name}`;
        skillsButton.classList.add("combatButton");
        controls.appendChild(skillsButton);
        skillsButton.addEventListener('click', () => {
                //get target
                let target = document.querySelector('.active');
                //if no target send alert
                if (!target) {
                    alert('No active target selected.');
                    return;
                }
                //remove all other targets
                document.querySelectorAll('.uiBox').forEach(box => {
                    if (box !== target) {
                      box.removeAttribute('data-skill-active');
                    }
                  });
                //add target
                target.dataset.skillActive = `${item.name}`;
                //get enemy name / display message to players message
                const enemyName =  target.getAttribute('data-name');
                addMessage(0, `You have targeted ${enemyName} with ${skills.name}`)
            })
    }
    //back button
    const backButton = document.createElement('button');
    backButton.id = 'backBtn';
    backButton.textContent = "Go Back";
    backButton.classList.add("combatButton");
    controls.appendChild(backButton);
    backButton.addEventListener('click', () => {
        combatControls(enemies);
    })

}



// ALL DAMAGE AND HEALING CALCS
async function calcDamageHealing(data, userStats) {
    const attack = data.attack;
    const skill = data.skill;
    //console.log(attack);
    //console.log(skill)
    //console.log(character);

    // Use fallback to 0 if any field is undefined
    const baseDamage = ((attack?.damage || 0) * (attack?.damage_mod || 1)) * (attack?.efficiency || 1);
    const skillBonusDamage = ((skill?.damage || 0) * (skill?.damage_modifier || 0) ) * (skill?.efficiency || 1);
    //console.log(`base damage = ${baseDamage}, skill damage=${skillBonusDamage}`);
    const totalDamage = baseDamage + skillBonusDamage;

    const baseHealing = ((attack?.healing || 0) * (attack?.healing_mod || 1)) * (attack?.efficiency || 1);
    const skillBonusHealing = (skill?.healing_modifier || 0) * (skill?.efficiency || 1);

    const totalHealing = baseHealing + skillBonusHealing;

    return {
        total_damage: Math.round(totalDamage),
        base_damage: Math.round(baseDamage),
        skill_damage: Math.round(skillBonusDamage),
        healing: Math.round(totalHealing),
    };

}



async function getDefense(){
    let grabbedValues = await grabInfo('get', 'getDefense');

    const { equipDefense, equipModifier, standbyDefense, standbyModifier, dexterity } = grabbedValues.message;

    const data = {
        "defense": equipDefense,
        "defenseModifier": equipModifier,
        "dexterity": dexterity,
    }
    return data
}



async function enemiesTurn(block, enemies) {
    //make indexes for messages
    let indexes = [];
    for (let i = 0; i < enemies.length; i++) {
        indexes.push(i);
    }
    //console.log(enemies);



    const enemyData = await grabInfo("post", "enemyData", enemies);
    const character = await grabInfo("get", "character");
    //console.log(character);
    //console.log(enemyData);
    if (block) {
        const data = block;
        console.log("block");
    }
    else if (!block) {
        //console.log(`NO BLOCK ${enemies}`);
        const enemyArray = Object.values(enemyData);

        let damageArray = [];
        let weaponSpeedArray = [];
        let enemyDexArray = [];
        //console.log(enemyArray);
        enemyArray.forEach((enemy, index) => {
             // no magic
             if(enemy.enemy_magic === null) {
                let damage;
                // get values
                const weapon = enemy.enemy_weapon_name;
                const weapon_critical = enemy.enemy_weapon_critical;
                const weapon_damage = enemy.enemy_weapon_damage;
                const base_damage = enemy.enemy_base_damage;

                const weapon_speed = enemy.enemy_weapon_speed;
                const dex_speed = enemy.enemy_dexterity;

                if (weapon_critical === 0) {
                    damage = (weapon_damage);
                }
                else {
                    damage = (weapon_damage * weapon_critical);
                }
                damageArray.push(damage + base_damage);
                weaponSpeedArray.push(weapon_speed);
                enemyDexArray.push(dex_speed);
             }
             else if(enemy.enemy_weapon_name === null) {
                let damage;
                // get values
                const magic = enemy.enemy_magic;
                const magic_special = enemy.enemy_weapon_critical;
                const magic_damage = enemy.enemy_weapon_damage;
                const base_damage = enemy.enemy_base_damage;

                const enemy_mana = enemy.enemy_mana;
                const dex_speed = enemy.enemy_dexterity;

                if (magic_special === 0) {
                    damage = (magic_damage);
                }
                else {
                    damage = (magic_damage * magic_special);
                }
                damageArray.push(damage + base_damage);
                weaponSpeedArray.push(weapon_speed);
                enemyDexArray.push(dex_speed);
             }
             else {
                let damage;
                // get values
                //magic
                const magic = enemy.enemy_magic;
                const magic_special = enemy.enemy_weapon_critical;
                const magic_damage = enemy.enemy_weapon_damage;
                //weapon
                const weapon = enemy.enemy_weapon_name;
                const weapon_critical = enemy.enemy_weapon_critical;
                const weapon_damage = enemy.enemy_weapon_damage;
                //base
                const base_damage = enemy.enemy_base_damage;
                //speed
                const weapon_speed = enemy.enemy_weapon_speed;
                //mana and dex
                const enemy_mana = enemy.enemy_mana;
                const dex_speed = enemy.enemy_dexterity;

                if (magic_special === 0 || weapon_critical === 0) {
                    damage = ((magic_special ?? 0) + (weapon_damage ?? 0));
                }
                else {
                    damage = ((magic_damage * magic_special) + (weapon_damage * weapon_critical));
                }

                //push to array
                damageArray.push(damage + base_damage);
                weaponSpeedArray.push(weapon_speed);
                enemyDexArray.push(dex_speed);
             }
        });
        //console.log(damageArray);
        // console.log(weaponSpeedArray);
        //console.log(`enemy dex: ${enemyDexArray}`);

        //DEX TEST FOR DODGE
        let playerDex = character.character.dexterity;
        //add armor modifiers to player dex
        character.characterArmor.forEach(item => {
            playerDex = playerDex * item.dexterity;
        })

        // here is the damage applied to player and pass dex
        let passDexArray = [];
        let deal_damage = [];
        for (let i = 0; i < enemyDexArray.length; i++) {
            if (playerDex > (enemyDexArray[i] * weaponSpeedArray[i])) {
                deal_damage.push(0);
                passDexArray.push(true);
            }
            else{
                deal_damage.push(damageArray[i]);
                passDexArray.push(false);
            }
        }

        // apply damage or alert
        if (deal_damage.length === 0) {
            alert("All enemies missed");
        }
        else {
            //sums up
            let sum = deal_damage.reduce((total, num) => total + num, 0);
            healthFun(0, sum, false, 'Lydia')
            for (let i = 0; i < passDexArray.length; i++) {
                if (passDexArray[i] === true) {
                    addMessage(1, `${enemies[i]} missed their target!`, targetName=`${enemies[i]}`, index=indexes[i])
                }
                else{
                    addMessage(1, `${enemies[i]} dealt ${deal_damage[i]} damage!`, targetName=`${enemies[i]}`, index=indexes[i])
                }
            }
        }
    }
}




// Used to finish your round
async function finishRound(block, enemies) {
    const enemyTeam = enemies;
    if (block) {
        let defense = await getDefense(character);
        addMessage(0, `You block these next attacks! Your defense is ${defense.defense}`);
        enemiesTurn(defense, enemies);
    }
    else if (!block) {

        //get divs affected
        const targetSkill = document.querySelector('.uiBox[data-skill-active]');
        const targetAttack = document.querySelector('.uiBox[data-attack-active]');

        const enemyNameDamage =  targetAttack?.getAttribute('data-name');
        const enemyNameSkill =  targetSkill?.getAttribute('data-name');

        const health = targetAttack?.querySelector(`span[id^="health-${enemyNameDamage.toLowerCase()}-"]`);
        const healthSkill = targetSkill?.querySelector(`span[id^="health-${enemyNameSkill.toLowerCase()}-"]`);


        let numberPartDamage;
        let numberPartSkill;
        //health == damage / healthSKill == skill target
        if (health) {
          const id = health.id;  // ex "health-orc-1"

          const match = id.match(/(\d+)$/);  // Regex: digits at the end
          if (match) {
            numberPartDamage = match[1];     // number
            //const prefixPart = id.replace(/(\d+)$/, '');  // "health-orc-"
            //console.log(`Prefix: ${prefixPart}, Number: ${numberPart}`);
          }
        }
        if (healthSkill) {
            const id = healthSkill.id;  // ex "health-orc-1"

            const match = id.match(/(\d+)$/);  // Regex: digits at the end
            if (match) {
              numberPartSkill = match[1];     // number
              //const prefixPart = id.replace(/(\d+)$/, '');  // "health-orc-"
              //console.log(`Prefix: ${prefixPart}, Number: ${numberPart}`);
            }
        }
        //console.log(`Number: ${numberPartDamage}, NumberSKill: ${numberPartSkill}`);

        //get skill and attack name
        let attackValue = targetAttack?.getAttribute('data-attack-active');
        let skillValue = targetSkill?.getAttribute('data-skill-active');

        //grab objects
        let grabbedValues = await grabInfo('post', 'finishRoundValues', {'attackValue': attackValue, 'skillValue': skillValue});

        //console.log("Grabbed Value =", grabbedValues);
        //console.log(enemyName);
        let nextMove = await calcDamageHealing(grabbedValues, character);

        if (targetAttack && targetSkill) {
            // checks if both attack and skill is used
            if (targetAttack == targetSkill) {
                // only one enemy is targeted with both
                alert(`You dealt ${nextMove.total_damage} damage to ${enemyNameDamage}!`);
                await healthFun(1, nextMove.total_damage, 1, targetName=enemyNameDamage, index=numberPartDamage, enemies);
               // console.log(`enemies ${enemies}`)
                enemiesTurn(false, enemies);


            } else {
                //different enemies are targeted 1, 1
                alert(`You dealt ${nextMove.base_damage} damage to ${enemyNameDamage} and ${nextMove.skill_damage} damage to ${enemyNameSkill}!`);

                await healthFun(1, nextMove.base_damage, 1, targetName=enemyNameDamage, index=numberPartDamage, enemies);
                await healthFun(1, nextMove.skill_damage, 1, targetName=enemyNameSkill, index=numberPartSkill, enemies);
                enemiesTurn(false, enemies);


            }
        } else if (targetAttack || targetSkill){
            //one or the other
            if (targetAttack){
                alert(`You dealt ${nextMove.base_damage} damage to ${enemyNameDamage}!`);
                await healthFun(1, nextMove.base_damage, 1, targetName=enemyNameDamage, index=numberPartDamage, enemies);
                enemiesTurn(false, enemies);

            } else {
                alert(`You dealt ${nextMove.skill_damage} damage to ${enemyNameSkill}!`);
                await healthFun(1, nextMove.skill_damage, 1, targetName=enemyNameSkill, index=numberPartSkill, enemies);
                enemiesTurn(false, enemies);

            }
        }
    }
}


// starts the combat and returns promise once its done
function startCombat(enemyHealth, enemyName) {
  //console.log("startCombat: setting up promise");
  return new Promise((resolve) => {
    combatEndCallback = resolve;
    //remove all npcs for combat
    const characterDiv = document.querySelector('.characterContainer');
    characterDiv.style.display = 'none';


    createEnemyBox(enemyHealth, enemyName, enemyName.length);
  });
}


//function to stop combat and go back to story mode
async function stopCombat() {
  //console.log("stopCombat called", combatEndCallback);
  if (typeof combatEndCallback === "function") {
    combatEndCallback();
    combatEndCallback = null;
    setTimeout(addNextButton, 3000);

  } else {
    console.warn("stopCombat called but no valid callback");
  }
}





// WILL ACTIVATE FIGHT MODE
// make enemy boxes is first
async function battleMode(enemies){
    const uiBox = document.querySelectorAll('.uiBox');
    //combatControls starts the combat UI

    combatControls(enemies)
    clickActive(uiBox);
    addMessage(0, "Enemies approach!", targetName='player', index=0)
    //gameLoop();
}


//NOT USED
async function gameLoop() {
    let skillTarget = document.querySelector('.uiBox[data-attack-active]');
    console.log(`TARGET SELECTED ${skillTarget}`);


    setTimeout(gameLoop, 2000);
}


async function deadMode(character){
    alert(`${character} has died. Their soul is put to rest.`);
    setTimeout(() => {
        window.location.href = `/dead/${character}/`;
    }, 400);

}


//BELOW IS FOR STORY ASPECT!

//makes the controls, dont use
function storyControls(choices) {
    const controls = document.getElementById('controls');
    controls.textContent = '';
    for (let i = 0; i < choices.length; i++) {
        const button = document.createElement('button');
        button.textContent = choices[i].text;
        button.addEventListener('click', function() {
            console.log('Next scene:', choices[i].next_scene);
        });
        controls.appendChild(button);
    }
}



function addNextButton() {
    //alert("Starting next button")
    const controls = document.getElementById('controls');
    controls.textContent = '';
    const nextButton = document.createElement('button');
    nextButton.id = 'next-btn';
    nextButton.textContent = 'Next';
    nextButton.style.display = 'inline';
    controls.appendChild(nextButton);
    document.getElementById("next-btn").addEventListener("click", showNextDialogueLine);
    const characterDiv = document.querySelector('.characterContainer');
    characterDiv.style.display = 'flex';
}


//this grabs the first quest, preloads it for JS and goes from ther
function startQuest() {
    const quest = document.querySelector('meta[name="quest"]').content;

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'quest',
            'X-Custom-Message-Quest': quest,
            'X-Custom-User': username
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


        const questCharacter = responseData.quest.content.character;
        const questCharacterURL = responseData.quest.content.characterURL;
        //console.log(responseData.quest.content.dialogue)
        dialogueLines = responseData.quest.content.dialogue;
        //console.log(dialogueLines)
        //console.log("DOwn")
        choices = responseData.quest.content.choices;
        currentLineIndex = 0;

       // console.log(responseData);

        createCharacterElement(questCharacterURL, questCharacter);  // Only sets image now
        showNextDialogueLine();  // Show the first line
    })

}


// displays player's dialogue
async function showNextDialogueLine() {
  const messageBoxes = document.querySelectorAll(".characterMessage");
  const nextBtn = document.getElementById("next-btn");
  //console.log(messageBoxes);

  if (currentLineIndex >= dialogueLines.length) {
    nextBtn.style.display = "none";
    showChoices();
    return;
  }

  // Clear all message boxes
  messageBoxes.forEach(box => box.textContent = "");

  const { line: lineText, character: characterName } = dialogueLines[currentLineIndex];
  //console.log(`characterName is ${characterName}`);
 // console.log(enemyScene);

  if (characterName === 'Enemy') {
    //console.log(`enemyList: ${enemyList}`);
    try {
      const info = await grabInfo("post", "enemyData", enemyList);
      let enemyName = [];
      let enemyHealth = [];

      info.forEach(item => {
        enemyName.push(item.enemy_name);
        enemyHealth.push(item.enemy_health);
      });

      alert("Enemies appear!");
      //alert(`enemyHealth=${enemyHealth}, enemyName=${enemyName}, length=${enemyName.length}`);

      // Await combat to finish
      await startCombat(enemyHealth, enemyName);

    } catch (error) {
      console.error(error);
    }
  } else {
    // Display dialogue line in matching box
    messageBoxes.forEach(box => {
      const boxCharacterName = box.id.replace("message-", "");
      if (boxCharacterName === characterName) {
        box.textContent = lineText;
      }
    });
  }

  currentLineIndex++;

  if (currentLineIndex >= dialogueLines.length) {
    nextBtn.style.display = "none";
    showChoices();
  } else {
    nextBtn.style.display = "inline-block";
  }
}





//grabs the choices from the Json and displays them as buttons.
function showChoices() {
  const choicesDiv = document.getElementById("controls");
  const dialogueBox = document.querySelector(".characterMessage");
  choicesDiv.innerHTML = "";

  choices.forEach(choice => {
    const btn = document.createElement("button");
    btn.textContent = choice.text;
    btn.onclick = () => {
      // You can replace this with a scene loader or logic router
      alert(`You selected: "${choice.text}" → Next scene: ${choice.next_scene}`);
      getNextScene(choice.next_scene);
    };
    choicesDiv.appendChild(btn);
  });
}

// when the next scene is needed it will go and grab it then play loop again.
function getNextScene(next_scene) {
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'quest',
            'X-Custom-Message-Quest': next_scene,
            'X-Custom-User': username
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
        //resets enemyScene Not all scenes have enemies
        enemyScene = false;
        enemyList = [];

        //rebuild the next button for dialogue
        const controls = document.getElementById('controls');
        controls.textContent = '';
        const nextButton = document.createElement('button');
        nextButton.id = 'next-btn';
        nextButton.textContent = 'Next';
        nextButton.style.display = 'none';
        controls.appendChild(nextButton);
        document.getElementById("next-btn").addEventListener("click", showNextDialogueLine);


        //assign variables
        const nextQuest = document.querySelector('meta[name="nextQuest"]').content;
        if (responseData.quest.content.choices.length == 1) {
            nextQuest.content = responseData.quest.content.choices[0].next_scene;
        }
        if (responseData.quest.content.enemies) {
            enemyScene = true;
            enemyList = responseData.quest.content.enemies
        }

        const questCharacter = responseData.quest.content.character;
        const questCharacterURL = responseData.quest.content.characterURL;
        dialogueLines = responseData.quest.content.dialogue;
        //console.log(dialogueLines)
        //console.log("UP")
        choices = responseData.quest.content.choices;

        //if (responseData)
        currentLineIndex = 0;

        //console.log(responseData);
        createCharacterElement(questCharacterURL, questCharacter);  // Only sets image now

        showNextDialogueLine();  // Show the first line
    })
}


//starts the main quest and adds event listener to progress dialogue
startQuest()
document.getElementById("next-btn").addEventListener("click", showNextDialogueLine);
