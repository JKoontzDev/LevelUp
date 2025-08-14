const buttons = document.querySelectorAll('.detail-button');
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const username = document.querySelector('meta[name="username"]').content;
const url = `/dashboard/${username}/ironstead/training/grab`;
const detailsSection = document.getElementById('detailsSection');
const playerLevel = document.querySelector('meta[name="level"]').content;
const weaponSelect = document.getElementById('weapon-select');
const magicSelect = document.getElementById('magic-select');
const characterMessage = document.getElementById('characterMessage');
const detailsButton = document.getElementById('details-button');
const detailsButtonM = document.getElementById('details-button-magic');

const motivation = document.querySelector('meta[name="motivation"]').content;




weaponSelect.addEventListener('change', function() {
  const selectedWeapon = weaponSelect.value;

  if (selectedWeapon) {
    detailsButton.setAttribute('data-action', `${selectedWeapon}`);
  } else {
    detailsButton.setAttribute('data-action', 'stat-details');
  }
});

magicSelect.addEventListener('change', function() {
  const selectedMagic = magicSelect.value;

  if (selectedMagic) {
    detailsButtonM.setAttribute('data-action', `${selectedMagic}`);
  } else {
    detailsButtonM.setAttribute('data-action', 'stat-details');
  }
});


function message(message) {
    characterMessage.textContent = `${message}`;
}




function addSkillDiv(skill, skillSet) {
    if (skill.skill_type == "combat") {
        const div = document.createElement('div');
        div.id = `${skill.name}`;
        div.className = 'div-details';
        // Skill name with icon
        const name = document.createElement('h3');
        name.textContent = `${skill.name}`;
        name.className = 'skill-name';
        const skillIcon = document.createElement('span');
        skillIcon.className = 'skill-icon';
        skillIcon.textContent = '★'; // Example icon
        name.prepend(skillIcon);
        div.appendChild(name);

        // Skill description
        const description = document.createElement('p');
        description.textContent = `${skill.description}`;
        description.className = 'skill-description';
        div.appendChild(description);

        // Damage modifier
        const damage = document.createElement('p');
        damage.textContent = `+${
          skillSet[0] && skillSet[0].damage_modifier != null
            ? skillSet[0].damage_modifier.toFixed(1)
            : skill.damage.toFixed(1)
        } damage modifier`;
        damage.className = 'skill-damage';
        div.appendChild(damage);



        // Level
        const level = document.createElement('div');
        level.className = 'skill-level';
        const levelText = document.createElement('p');
        levelText.textContent = `Required level: ${skill.level_required}`;
        levelText.className = 'level-text';
        level.appendChild(levelText);

        // progress bar
        const progressBarContainer = document.createElement('div');
        progressBarContainer.className = 'progress-bar-container';
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.style.width = `${Math.min((playerLevel / skill.level_required) * 100, 100)}%`;
        progressBarContainer.appendChild(progressBar);
        level.appendChild(progressBarContainer);

        div.appendChild(level);

        // efficiency
        const efficiency = document.createElement('div');
        efficiency.className = 'skill-level';
        const efficiencyText = document.createElement('p');
        efficiencyText.textContent = `Efficiency: ${skillSet[0] && skillSet[0].efficiency ? skillSet[0].efficiency : 0}`;
        efficiencyText.className = 'level-text';
        efficiencyText.id = 'efficiencyText';

        efficiency.appendChild(efficiencyText);

        // progress bar
        const eprogressBarContainer = document.createElement('div');
        eprogressBarContainer.className = 'e-progress-bar-container';
        const eprogressBar = document.createElement('div');
        eprogressBar.className = 'e-progress-bar';
        eprogressBar.style.width = `${(skillSet[0] && skillSet[0].efficiency ? skillSet[0].efficiency : 0) / 10 * 100}%`;
        eprogressBarContainer.appendChild(eprogressBar);
        efficiency.appendChild(eprogressBarContainer);

        div.appendChild(efficiency);

        //learn button
        const actionButton = document.createElement('button');
        actionButton.textContent = 'Learn Skill';
        actionButton.className = 'action-button';
        actionButton.id = 'learn-button';

        if (playerLevel < skill.level_required) {
            actionButton.disabled = true;
            actionButton.textContent = "Not high enough level";
            actionButton.className = 'action-button disabled';
        } else if (motivation <= 0) {
            actionButton.disabled = true;
            actionButton.textContent = "Out of motivation";
            actionButton.className = 'action-button disabled';
        } else if (skillSet[0].efficiency === 10){
            actionButton.disabled = true;
            actionButton.textContent = "Maxed Out";
            actionButton.className = 'action-button disabled';
        }else {
            actionButton.addEventListener('click', () => {
            sendSkill(`${skill.name}`)
            });
        }

        div.appendChild(actionButton);

        //close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.className = 'action-button danger';
        closeButton.addEventListener('click', () => {
            div.remove();
        });
        div.appendChild(closeButton);

        detailsSection.appendChild(div);
    }
    else if (skill.skill_type == "general") {
        console.log(skill);
        console.log(skillSet);
        const div = document.createElement('div');
        div.id = `${skill.name}`;
        div.className = 'div-details';
        // Skill name with icon
        const name = document.createElement('h3');
        name.textContent = `${skill.name}`;
        name.className = 'skill-name';
        const skillIcon = document.createElement('span');
        skillIcon.className = 'skill-icon';
        skillIcon.textContent = '★'; // Example icon
        name.prepend(skillIcon);
        div.appendChild(name);

        // Skill description
        const description = document.createElement('p');
        description.textContent = `${skill.description}`;
        description.className = 'skill-description';
        div.appendChild(description);


        // Level
        const level = document.createElement('div');
        level.className = 'skill-level';
        const levelText = document.createElement('p');
        levelText.textContent = `Required level: ${skill.level_required}`;
        levelText.className = 'level-text';
        level.appendChild(levelText);

        // progress bar
        const progressBarContainer = document.createElement('div');
        progressBarContainer.className = 'progress-bar-container';
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.style.width = `${Math.min((playerLevel / skill.level_required) * 100, 100)}%`;
        progressBarContainer.appendChild(progressBar);
        level.appendChild(progressBarContainer);

        div.appendChild(level);

        // efficiency
        const efficiency = document.createElement('div');
        efficiency.className = 'skill-level';
        const efficiencyText = document.createElement('p');
        efficiencyText.textContent = `Efficiency: ${skillSet && skillSet[0].efficiency ? skillSet[0].efficiency : 0}`;
        efficiencyText.className = 'level-text';
        efficiencyText.id = 'efficiencyText';

        efficiency.appendChild(efficiencyText);

        // progress bar
        const eprogressBarContainer = document.createElement('div');
        eprogressBarContainer.className = 'e-progress-bar-container';
        const eprogressBar = document.createElement('div');
        eprogressBar.className = 'e-progress-bar';
        console.log(skillSet[0].efficiency);
        eprogressBar.style.width = `${(skillSet && skillSet[0].efficiency ? skillSet[0].efficiency : 0) / 10 * 100}%`;
        eprogressBarContainer.appendChild(eprogressBar);
        efficiency.appendChild(eprogressBarContainer);
        div.appendChild(efficiency);

        //learn button
        const actionButton = document.createElement('button');
        actionButton.textContent = 'Learn Skill';
        actionButton.className = 'action-button';
        actionButton.id = 'learn-button';

        if (playerLevel < skill.level_required) {
            actionButton.disabled = true;
            actionButton.textContent = "Not high enough level";
            actionButton.className = 'action-button disabled';
        } else if (motivation <= 0) {
            actionButton.disabled = true;
            actionButton.textContent = "Out of motivation";
            actionButton.className = 'action-button disabled';
        } else if (skillSet[0].efficiency === 10){
            actionButton.disabled = true;
            actionButton.textContent = "Maxed Out";
            actionButton.className = 'action-button disabled';
        }else {
            actionButton.addEventListener('click', () => {
            sendSkill(`${skill.name}`)
            });
        }

        div.appendChild(actionButton);

        //close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.className = 'action-button danger';
        closeButton.addEventListener('click', () => {
            div.remove();
        });
        div.appendChild(closeButton);

        detailsSection.appendChild(div);

    }
    else if (skill.skill_type == "motivational") {
        const div = document.createElement('div');
        div.id = `${skill.name}`;
        div.className = 'div-details';
        // Skill name with icon
        const name = document.createElement('h3');
        name.textContent = `${skill.name}`;
        name.className = 'skill-name';
        const skillIcon = document.createElement('span');
        skillIcon.className = 'skill-icon';
        skillIcon.textContent = '★'; // Example icon
        name.prepend(skillIcon);
        div.appendChild(name);

        // Skill description
        const description = document.createElement('p');
        description.textContent = `${skill.description}`;
        description.className = 'skill-description';
        div.appendChild(description);

         // healing modifier
        const healing = document.createElement('p');
        healing.textContent = `+${
          skillSet[0] && skillSet[0].healing_modifier != null
            ? skillSet[0].healing_modifier.toFixed(1)
            : skill.healing.toFixed(1)
        } healing modifier`;
        healing.className = 'skill-healing';
        div.appendChild(healing);

        // Level
        const level = document.createElement('div');
        level.className = 'skill-level';
        const levelText = document.createElement('p');
        levelText.textContent = `Required level: ${skill.level_required}`;
        levelText.className = 'level-text';
        level.appendChild(levelText);

        // progress bar
        const progressBarContainer = document.createElement('div');
        progressBarContainer.className = 'progress-bar-container';
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.style.width = `${Math.min((playerLevel / skill.level_required) * 100, 100)}%`;
        progressBarContainer.appendChild(progressBar);
        level.appendChild(progressBarContainer);

        div.appendChild(level);

        // efficiency
        const efficiency = document.createElement('div');
        efficiency.className = 'skill-level';
        const efficiencyText = document.createElement('p');
        efficiencyText.textContent = `Efficiency: ${skillSet && skillSet[0].efficiency ? skillSet[0].efficiency : 0}`;
        efficiencyText.className = 'level-text';
        efficiencyText.id = 'efficiencyText';

        efficiency.appendChild(efficiencyText);

        // progress bar
        const eprogressBarContainer = document.createElement('div');
        eprogressBarContainer.className = 'e-progress-bar-container';
        const eprogressBar = document.createElement('div');
        eprogressBar.className = 'e-progress-bar';
        eprogressBar.style.width = `${(skillSet && skillSet[0].efficiency ? skillSet[0].efficiency : 0) / 10 * 100}%`;
        eprogressBarContainer.appendChild(eprogressBar);
        efficiency.appendChild(eprogressBarContainer);

        div.appendChild(efficiency);

        //learn button
        const actionButton = document.createElement('button');
        actionButton.textContent = 'Learn Skill';
        actionButton.className = 'action-button';
        actionButton.id = 'learn-button';

        if (playerLevel < skill.level_required) {
            actionButton.disabled = true;
            actionButton.textContent = "Not high enough level";
            actionButton.className = 'action-button disabled';
        } else if (motivation <= 0) {
            actionButton.disabled = true;
            actionButton.textContent = "Out of motivation";
            actionButton.className = 'action-button disabled';
        } else if (skillSet[0].efficiency === 10){
            actionButton.disabled = true;
            actionButton.textContent = "Maxed Out";
            actionButton.className = 'action-button disabled';
        }else {
            actionButton.addEventListener('click', () => {
            sendSkill(`${skill.name}`)
            });
        }

        div.appendChild(actionButton);

        //close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.className = 'action-button danger';
        closeButton.addEventListener('click', () => {
            div.remove();
        });
        div.appendChild(closeButton);

        detailsSection.appendChild(div);


    }
}


function addWeaponDiv(weaponBag, data) {
        const div = document.createElement('div');
        div.id = `${data.weapon_name}`;
        div.className = 'div-details';

        // Skill name with icon
        const name = document.createElement('h3');
        name.textContent = `${data.weapon_name}`;
        name.className = 'skill-name';
        const skillIcon = document.createElement('span');
        skillIcon.className = 'skill-icon';
        skillIcon.textContent = '★'; // Example icon
        name.prepend(skillIcon);
        div.appendChild(name);

        // Skill description
        const description = document.createElement('p');
        description.textContent = `${data.weapon_desc}`;
        description.className = 'skill-description';
        div.appendChild(description);

        // Damage modifier
        const damage = document.createElement('p');
        damage.textContent = `Damage Modifier: ${weaponBag[0].damage_modifier.toFixed(1)}`;
        damage.className = 'skill-damage';
        div.appendChild(damage);

        // efficiency modifier
        const efficiency = document.createElement('p');
        efficiency.textContent = `Current efficiency: ${weaponBag[0].efficiency}`;
        efficiency.id = 'itemEfficiency';
        efficiency.className = 'skill-damage';
        div.appendChild(efficiency);

        // safe/intense train
        const trainingSelect = document.createElement('select');
        trainingSelect.className = 'training-select';
        const options = [
            { value: 'safe', text: 'Safe Training (Low Risk, Low Reward)' },
            { value: 'intense', text: 'Intense Training (High Risk, High Reward)' }
        ];

        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.text;
            trainingSelect.appendChild(option);
        });

        div.appendChild(trainingSelect);



        //learn button
        const actionButton = document.createElement('button');
        actionButton.textContent = 'Practice Weapon';
        actionButton.className = 'action-button';

        if (motivation <= 0) {
            actionButton.disabled = true;
            actionButton.textContent = "Out of motivation";
            actionButton.className = 'action-button disabled';
            message("I just can't right now");

        } else {
            actionButton.addEventListener('click', () => {
            const selectedTraining = trainingSelect.value;
            data = {
                "name": div.id,
                "trainType": selectedTraining,
            }
            message("Let's do this!");

            sendWeapon(data)
        });
        }
        div.appendChild(actionButton);

        //close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.className = 'action-button danger';
        closeButton.addEventListener('click', () => {
            div.remove();
        });
        div.appendChild(closeButton);

        detailsSection.appendChild(div);
}


function addMagicDiv(magic, magicTome) {
        const div = document.createElement('div');
        div.id = `${magicTome.magic_name}`;
        div.className = 'div-details';

        // Skill name with icon
        const name = document.createElement('h3');
        name.textContent = `${magicTome.magic_name}`;
        name.className = 'skill-name';
        const skillIcon = document.createElement('span');
        skillIcon.className = 'skill-icon';
        skillIcon.textContent = '★'; // Example icon
        name.prepend(skillIcon);
        div.appendChild(name);

        // Skill description
        const description = document.createElement('p');
        description.textContent = `${magicTome.magic_desc}`;
        description.className = 'skill-description';
        div.appendChild(description);

        // Damage modifier
        const damage = document.createElement('p');
        damage.textContent = `Current Damage: ${magic[0].damage_modifier}`;
        damage.className = 'skill-damage';
        div.appendChild(damage);

        // efficiency modifier
        const efficiency = document.createElement('p');
        efficiency.textContent = `Current efficiency: ${magic[0].efficiency}`;
        efficiency.id = 'itemEfficiency';
        efficiency.className = 'skill-damage';
        div.appendChild(efficiency);

        // safe/intense train
        const trainingSelect = document.createElement('select');
        trainingSelect.className = 'training-select';
        const options = [
            { value: 'safe', text: 'Safe Training (Low Risk, Low Reward)' },
            { value: 'intense', text: 'Intense Training (High Risk, High Reward)' }
        ];

        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.text;
            trainingSelect.appendChild(option);
        });

        div.appendChild(trainingSelect);



        //learn button
        const actionButton = document.createElement('button');
        actionButton.textContent = 'Practice Magic';
        actionButton.className = 'action-button';

        if (motivation <= 0) {
            actionButton.disabled = true;
            actionButton.textContent = "Out of motivation";
            actionButton.className = 'action-button disabled';
            message("I just can't right now");

        } else {
            actionButton.addEventListener('click', () => {
            const selectedTraining = trainingSelect.value;
            data = {
                "name": div.id,
                "trainType": selectedTraining,
            }
            message("Let's do this!");
            sendMagic(data)
        });
        }
        div.appendChild(actionButton);

        //close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.className = 'action-button danger';
        closeButton.addEventListener('click', () => {
            div.remove();
        });
        div.appendChild(closeButton);

        detailsSection.appendChild(div);
}





// post
function sendSkill(message) {
    //console.log(message)

    data = {"message": message}
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': "skill",
            'X-Custom-User': username
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
        //console.log(responseData);
        if (responseData.result){
            //get the mods from the response data
            const damageMod = responseData.result.damage;
            const healingMod = responseData.result.healing;
            // query the <p>
            const damage = document.querySelector('.skill-damage');
            const healing = document.querySelector('.skill-healing');

            const Eprogress = document.querySelector('.e-progress-bar');
            const efficiencyText = document.getElementById('efficiencyText');
            const motText = document.getElementById("motText");
            const actionButton = document.querySelector('.action-button');
            if (responseData.currentMotivation <= 0) {
                actionButton.disabled = true;
                actionButton.textContent = "Out of motivation";
                actionButton.className = 'action-button disabled';
            }
            motText.textContent = `${responseData.currentMotivation}/${responseData.maxMotivation}`;

            efficiencyText.textContent = `Efficiency: ${responseData.result.efficiency}`
            Eprogress.style.width = `${(responseData.result.efficiency / 10) * 100}%`;
            if (damageMod) {
                damage.textContent = `+${damageMod.toFixed(1)} damage modifier`;
            }
            else if (healingMod){
                healing.textContent = `+${healingMod.toFixed(1)} healing modifier`;
            }
        } else {
            const learnButton = document.getElementById('learn-button');
            learnButton.textContent = "Maxed Out";
            learnButton.disabled = true;

        }


    })
}


function sendWeapon(data){
    data = {"name": data.name, "trainType": data.trainType}
    //console.log(data);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': "weapon",
            'X-Custom-User': username
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
        //console.log(responseData);
        if (responseData.message == "You died") {
            if (responseData.redirect) {
              window.location.href = responseData.redirect;
          }
        } else {
            const heathText = document.getElementById("healthText");
            const motText = document.getElementById("motText");
            const itemEfficiency = document.getElementById("itemEfficiency");
            const damageMod = document.querySelector(".skill-damage");

            const actionButton = document.querySelector('.action-button');
            if (responseData.currentMotivation <= 0) {
                actionButton.disabled = true;
                actionButton.textContent = "Out of motivation";
                actionButton.className = 'action-button disabled';
            }

            healthText.textContent = `${responseData.currentHealth}/${responseData.maxHealth}`;
            motText.textContent = `${responseData.currentMotivation}/${responseData.maxMotivation}`;
            itemEfficiency.textContent = `Current efficiency: ${responseData.efficiency}`;
            message(responseData.message);
        }


    })
}


function sendMagic(data){
    data = {"name": data.name, "trainType": data.trainType}
    //alert("YOOOOO")
    console.log(data);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': "magic",
            'X-Custom-User': username
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
        //console.log(responseData);
         if (responseData.message == "You died") {
            if (responseData.redirect) {
              window.location.href = responseData.redirect;
            }
         } else {
            const heathText = document.getElementById("healthText");
            const motText = document.getElementById("motText");
            const itemEfficiency = document.getElementById("itemEfficiency");
            const actionButton = document.querySelector('.action-button');

            if (responseData.currentMotivation <= 0) {
                actionButton.disabled = true;
                actionButton.textContent = "Out of motivation";
                actionButton.className = 'action-button disabled';
            }
            healthText.textContent = `${responseData.currentHealth}/${responseData.maxHealth}`;
            motText.textContent = `${responseData.currentMotivation}/${responseData.maxMotivation}`;
            itemEfficiency.textContent = `Current efficiency: ${responseData.efficiency}`;
            message(responseData.message);
        }

    })

}


//MAIN BUTTONS


buttons.forEach(button => {
    button.addEventListener('click', (e) => {
        const action = e.target.dataset.action;
        const category = e.target.dataset.category;
        const name = e.target
        console.log(name);
        //console.log(action);
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Custom-Message': action,
                'X-Custom-Category': category,
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
            detailsSection.textContent = '';
            window.scrollTo({
              top: document.body.scrollHeight,
              behavior: 'smooth'
            });

            if (responseData.skill){
                const skillSet = responseData.skillSet;
                const skill = responseData.skill;
                addSkillDiv(skill, skillSet)
            } else if(responseData.weaponBag) {
                const weaponBag = responseData.weaponBag;
                const info = responseData.data
                addWeaponDiv(weaponBag, info)
            } else if (responseData.magic){
                const magic = responseData.magic;
                const info = responseData.magicTome
                addMagicDiv(magic, info)
            }
        })
    })
})
