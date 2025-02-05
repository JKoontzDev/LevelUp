const actions = {
    forge: ["Bring your finest materials, and I'll help you craft gear worthy of legends!",
    "Forge your destiny with weapons and armor built to conquer any challenge!",
    "The flames are ready—let's create something powerful and unstoppable!",
    "Choose your materials, and together we'll hammer out greatness!",
    "Every hero needs the right tools; let’s make yours extraordinary!",
    "The anvil awaits—let’s shape your strength into unstoppable power!",
    "Bring the steel, and I'll bring the skill; let’s forge your future!",
    "Your journey deserves the best—let’s craft weapons to carry you to victory!",
    "In the heat of the forge, even the smallest spark can become a blazing force!",
    "Lay down your materials, and I’ll turn them into masterpieces of might!"
    ],
    repair: [
    "Let’s restore your gear to its former glory—stronger and ready for battle!",
    "Bring me your damaged equipment, and I’ll make it good as new!",
    "A true hero's tools deserve care—let me repair them for the challenges ahead!",
    "Every scratch tells a story, but durability wins wars—let’s fix that up!",
    "Your gear has served you well; now, let me return the favor!",
    "Even the mightiest weapons need tending—let’s make yours battle-ready again!",
    "Trust me to breathe new life into your worn-out equipment!",
    "Durability is key to survival—hand over your gear, and I’ll restore its strength!",
    "Every great warrior knows the value of sharp, reliable tools—let’s repair yours!",
    "The journey is long—let me ensure your gear stands the test of time!"
],
    upgrade: [
    "Let’s unlock the true potential of your gear!",
    "Take your equipment to the next level—strength like never before!",
    "Every hero deserves powerful tools—let’s enhance yours!",
    "Strengthen your gear and prepare to conquer any challenge!",
    "Empower your equipment and rise above the rest!",
    "Transform ordinary tools into extraordinary weapons—let’s begin!",
    "Fortify your gear and claim the strength you deserve!",
    "Every upgrade brings you closer to greatness—enhance now!",
    "Sharpen your edge, reinforce your armor—let’s make you unstoppable!"
],
    smelt: [
    "Smelt raw materials into refined perfection!",
    "Turn ore into something truly magnificent!",
    "The forge is ready—let’s transform your resources into greatness!",
    "Raw materials are just the beginning; let’s smelt them into power!",
    "The first step to creation is transformation—start smelting now!",
    "Purify your materials and prepare for legendary crafting!",
    "Every masterpiece starts with molten metal—let’s smelt it right!",
    "From the fire, strength is born—smelt your ore into something remarkable!",
    "Forge the future by refining the raw—smelt your materials now!",
    "Let the flames purify your ore into pure potential!"
],
    smeltProcess: [
    "Ah, the fire sings as the ore transforms—this is where the magic begins!",
    "Feel the heat, smell the strength—greatness is being forged!",
    "Molten metal and roaring flames—nothing compares to this!",
    "The sound of progress, the smell of power—this is the forge at its best!",
    "Watch closely; this is how raw potential becomes legendary!",
    "The fire purifies, the hammer shapes—this is where champions are born!",
    "There's nothing like turning ore into something worth wielding!",
    "The forge never lies—here, effort and fire create true strength!",
    "Ore today, legends tomorrow—this is how it all begins!",
    "From the depths of the earth to the heat of the forge, greatness is in the making!"
],
    forged: [
    "Feel the power of creation as your equipment comes to life!",
    "The forge breathes, the hammer strikes—greatness is being made!",
    "Every strike of the hammer brings your destiny closer!",
    "From raw materials to glory—your new equipment awaits!",
    "The spark of creation ignites—prepare to wield something extraordinary!",
    "This is where heroes' tools are born—your gear is in good hands!",
    "With every strike, your future grows brighter—your gear is almost done!",
    "Steel and fire combine to craft your next step toward victory!",
    "The anvil speaks, the flames roar—your new gear is nearly here!"
],
    upgradeEquipmentDialogue: [
    "Your gear evolves—stronger and sharper than ever before!",
    "A touch of magic and mastery—your equipment is now even mightier!",
    "Feel the surge of power as your gear reaches new heights!",
    "The road to greatness is paved with upgrades—your equipment is ready!",
    "Every enhancement brings you closer to unrivaled strength!",
    "Steel and precision combine—your upgraded gear is unstoppable!",
    "With this upgrade, your enemies will tremble before you!",
    "The forge never lies—your equipment is now ready to conquer any challenge!",
    "Step into battle with confidence—your newly upgraded gear won't fail you!",
    "Greatness forged anew—your equipment is ready to shine!"
],
    repairEquipmentDialogue: [
    "Good as new—your gear is ready for the next adventure!",
    "Every crack mended, every dent gone—your equipment is battle-ready again!",
    "Repaired and reliable—your gear won’t let you down now!",
    "A little care goes a long way—your equipment is ready to shine!",
    "Your tools are restored—stronger than the day you got them!",
    "Every hero needs dependable gear—your repairs are complete!",
    "Your equipment’s back in peak condition—time to get back out there!",
    "Restored and reinforced—your gear can handle anything now!",
    "The wear and tear is gone—your equipment is as sturdy as ever!",
    "No more cracks or breaks—your gear is as strong as your resolve!"
]
};
const actionFunctions = {
    forgeFunction,
    repairFunction,
    upgradeFunction,
    smeltFunction
}

const actionContent = document.getElementById('actionContent');
const buttons = document.querySelectorAll('.action-btn');
const blackSmithText = document.querySelector('.blacksmith-greeting');
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const username = document.querySelector('meta[name="username"]').content;
const url = '/dashboard/${username}/ironstead/blacksmith/items';
const itemGrid = document.getElementById('actionContent');
const loading = document.getElementById('loading');
const upgradePanelDiv = document.getElementById("upgradePanel");



buttons.forEach(button => {
    button.addEventListener('click', (e) => {
        const action = e.target.dataset.action;
        blackSmithText.textContent = getRandomMessage(action);
        const functionName = `${action}Function`;
        if (actionFunctions[functionName]) {
            loading.style.display = 'block';
            itemGrid.textContent = '';
            upgradePanelDiv.style.display = 'none';
            setTimeout(() => {
                loading.style.display = 'none';
                actionFunctions[functionName](); // Call the function
            }, 1000);
        } else {
            console.log("Function not found!");
        }
    });
});



function getRandomMessage(action) {
    const Messages = actions[action];
    const randomIndex = Math.floor(Math.random() * Messages.length);
    return Messages[randomIndex];
}



function forgeFunction() {
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'forge',
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
        const items = responseData.items;
        const armor = responseData.forgeables;
        // below is used to add items panel
        const div = document.createElement('div');
        div.className = 'item';
        const itemName = document.createElement('h3');
        itemName.textContent = "Items in bag";
        div.appendChild(itemName);
        items.forEach(item => {
            const itemQuantity = document.createElement('p');
            itemQuantity.id = item.id
            itemQuantity.textContent = `${item.name}: ${item.quantity}`;
            itemQuantity.setAttribute('quantity', item.quantity);
            div.appendChild(itemQuantity);
        })
        itemGrid.appendChild(div);
        // above is used to add items panel
        // below is for armor
        armor.forEach(item =>{
            const div = document.createElement('div');
            div.id = `${item.id}${item.name}`;
            div.className = 'item';
            const itemName = document.createElement('h3');
            itemName.textContent = item.name;
            div.appendChild(itemName);
            item.ingredients.forEach(ingredient => {
                const itemQuantity = document.createElement('p');
                itemQuantity.textContent = `${ingredient.name}: ${ingredient.quantity}`;
                div.appendChild(itemQuantity);

            })
            const DBut = document.createElement('button');
            DBut.textContent = `Forge now`;
            DBut.id = `${item.name}`;
            DBut.classList.add('DButton');
            div.appendChild(DBut);
            DBut.addEventListener('click', function () {
                forgeSend(DBut.id);
            })
            itemGrid.appendChild(div);
        })
    })
}


function repairFunction() {
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'repair',
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
        const item = responseData.items;
        item.forEach(item =>{
            const div = document.createElement('div');
            div.id = `${item.id}${item.name}`;
            div.className = 'item';

            const itemName = document.createElement('h3');
            itemName.textContent = item.name;
            div.appendChild(itemName);

            const itemDur = document.createElement('h5');
            itemDur.textContent =`Max durability: ${item.max_durability}`;
            div.appendChild(itemDur);

            const itemCDur = document.createElement('h5');
            itemCDur.textContent =`Current durability: ${item.current_durability}`;
            div.appendChild(itemCDur);

            const itemPrice = document.createElement('p');
            itemPrice.textContent = `Repair cost: ${item.repair_cost} gold`;
            div.appendChild(itemPrice);

            const DBut = document.createElement('button');
            DBut.textContent = `Repair now`;
            DBut.id = `${item.name}`;
            DBut.classList.add('DButton');
            div.appendChild(DBut);

            if (item.current_durability == item.max_durability) {
                DBut.disabled = true;
                DBut.classList.add('strike');
            }

            DBut.addEventListener('click', function () {
                data = {
                    'name': item.name,
                    'message': 'repair',
                    'type': item.type,
                    'repair_cost': item.repair_cost,
                    'itemId': item.id
                }
                fetch(url, {
                    method: 'Post',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Custom-Message': 'repair',
                        'X-Custom-User': username,
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
                    const itemDurability = responseData.data;
                    const message = responseData.message;
                    if (message === "Insufficient funds") {
                        alert(`Insufficient funds to repair: ${item.name}`);
                    } else {
                        itemCDur.textContent =`Current durability: ${itemDurability.newDur}`;
                        alert(`Thanks for your service!`);
                        blackSmithText.textContent = getRandomMessage('upgradeEquipmentDialogue')
                        if (itemDurability.newDur == itemDurability.maxDur) {
                            DBut.disabled = true;
                            DBut.classList.add('strike');
                        }
                    }
                })
            })
            itemGrid.appendChild(div);
        })
    })
}


function smeltFunction() {
    const itemDiv = document.querySelector('.item');
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'smelt',
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
        if (responseData.backpack) {
            if (!itemDiv) {
                responseData.backpack.forEach(item =>{
                    let quantityF = item.quantity;
                    const div = document.createElement('div');
                    div.id = item.id;
                    div.className = 'item';

                    const itemName = document.createElement('h3');
                    itemName.textContent = item.name;
                    div.appendChild(itemName);

                    const itemQuantity = document.createElement('p');
                    itemQuantity.textContent = `Quantity: ${quantityF}`;
                    div.appendChild(itemQuantity);

                    const DBut = document.createElement('button');
                    DBut.textContent = `Smelt now`;
                    DBut.id = `${item.name}`;
                    DBut.classList.add('DButton');
                    div.appendChild(DBut);

                    DBut.addEventListener('click', function () {
                        if ((quantityF - 2) < 0) {
                            itemQuantity.textContent = "Sorry, not enough ore for a ingot.";
                            blackSmithText.textContent = "Sorry buddy, I can't make metal without all the ingredients!";
                            DBut.remove();
                            const itemQuantity2 = document.createElement('p');
                            itemQuantity2.textContent = `Quantity: ${quantityF}`;
                            div.appendChild(itemQuantity2);
                            quantityF = quantityF - 2;
                        } else {
                            quantityF = quantityF - 2;
                            itemQuantity.textContent = `Quantity: ${quantityF}`;
                            blackSmithText.textContent = getRandomMessage("smeltProcess");
                            const data = {
                                "OreName": itemName.textContent,
                                "OreId": div.id
                            }
                            fetch(url, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrfToken,
                                    'X-Custom-Message': 'smelt',
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
                            })
                        }
                    })
                    itemGrid.appendChild(div);
                })
            }
        }
    })
}


function upgradeFunction() {
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'upgrade',
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
        const item = responseData.items;
        const ingredients = responseData.ingredients;

        //bellow is to add ingredients

        const flexDiv = document.createElement("div");
        //div.id = `${item.id}${item.name}`;
        flexDiv.className = "flexDiv";

        const div = document.createElement('div');
        div.className = 'item';
        flexDiv.appendChild(div)

        const itemName = document.createElement('h3');
        itemName.textContent = "Items in bag";
        div.appendChild(itemName);

        ingredients.forEach(item => {
            const itemQuantity = document.createElement('p');
            itemQuantity.id = item.id
            itemQuantity.textContent = `${item.name}: ${item.quantity}`;
            itemQuantity.setAttribute('quantity', item.quantity);
            div.appendChild(itemQuantity);
        })
        itemGrid.appendChild(flexDiv);
        //above is to add ingredients
        //bellow is to add items

        item.forEach((item) => {
              const flexDiv = document.createElement("div");
              flexDiv.className = "flexDiv";

              const div = document.createElement("div");
              div.id = `${item.id}${item.name}`;
              div.className = "item";
              flexDiv.appendChild(div);

              const itemImage = document.createElement("img");
              itemImage.src = item.image || "default-item.png"; // Add item.image for dynamic icons
              itemImage.alt = `${item.name}`;
              itemImage.className = "item-icon";
              div.appendChild(itemImage);

              const itemName = document.createElement("h3");
              itemName.textContent = item.name;
              itemName.className = "item-name";
              div.appendChild(itemName);

              const DBut = document.createElement("button");
              DBut.textContent = `Upgrade Now`;
              DBut.id = `${item.name}`;
              DBut.classList.add("DButton");
              DBut.title = `Upgrade ${item.name} to the next level!`;
              div.appendChild(DBut);

              DBut.addEventListener("click", () => showUpgradePanel(item));

              itemGrid.appendChild(flexDiv);
        })
    })
}





function forgeSend(name) {
    const data = {
        status: 'sent',
        itemName: name,
    };
    fetch(url, {
        method: 'Post',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'forge',
            'X-Custom-User': username,
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
        if (responseData.ingredients) {
            items = responseData.ingredients;
            alert(`You forged: ${name}. This item was added to your inventory!`);
            items.forEach(item => {
                const itemPId = document.getElementById(item.id);
                const oldQuantity = itemPId.getAttribute('quantity');
                const newQuantity = oldQuantity - item.quantity;
                itemPId.textContent = `${item.name}: ${newQuantity}`;
                itemPId.setAttribute('quantity', newQuantity);
                blackSmithText.textContent = getRandomMessage('forged');
            })
        } else {
            blackSmithText.textContent = "Sorry buddy I can't make greatness without the proper ingredients!";
            const button = document.getElementById(name);
            alert(responseData.message);
            button.disabled = true;
            button.classList.add('strike');
        }
    })
}




function showUpgradePanel(item) {
  upgradePanelDiv.textContent = "";

  if (item.weaponLevel) {
      const title = document.createElement("h2");
      title.textContent = `Upgrade: ${item.name} Lv. ${item.weaponLevel.current_level} → Lv. ${item.weaponLevel.current_level + 1}`;
      upgradePanelDiv.appendChild(title);
  } else {
      const title = document.createElement("h2");
      title.textContent = `Upgrade: ${item.name} Lv. ${item.armorLevel.current_level} → Lv. ${item.armorLevel.current_level + 1}`;
      upgradePanelDiv.appendChild(title);
  }

  if (item.damage) {
      const statsDiv = document.createElement("div");
      statsDiv.className = "stats";
      statsDiv.textContent = `Attack: ${item.damage + item.updatedDam.upgraded_damage} → ${item.damage + item.updatedDam.upgraded_damage + 2}`;
      upgradePanelDiv.appendChild(statsDiv);
  } else {
      const statsDiv = document.createElement("div");
      statsDiv.className = "stats";
      statsDiv.textContent = `Defense: ${item.defense + item.updatedDen.upgraded_defense} → ${item.defense + item.updatedDen.upgraded_defense + 2}`;
      upgradePanelDiv.appendChild(statsDiv);
  }

  // Add ingredients section
  const ingredientsDiv = document.createElement("div");
  ingredientsDiv.className = "ingredients";

  const ingredientsTitle = document.createElement("h3");
  ingredientsTitle.textContent = "Required Ingredients";
  ingredientsDiv.appendChild(ingredientsTitle);

  const ingredientsList = document.createElement("ul");
  item.ingredients.forEach((ingredient) => {
    const listItem = document.createElement("li");
    listItem.textContent = `${ingredient.name}: ${ingredient.quantity - 1}`;
    ingredientsList.appendChild(listItem);
  });
  ingredientsDiv.appendChild(ingredientsList);
  upgradePanelDiv.appendChild(ingredientsDiv);

  const upgradeButton = document.createElement("button");
  upgradeButton.className = "upgrade-button";
  upgradeButton.textContent = "Upgrade";
  upgradeButton.addEventListener("click", () => handleUpgrade(item));
  upgradePanelDiv.appendChild(upgradeButton);

  const cancelButton = document.createElement("button");
  cancelButton.textContent = "Cancel";
  cancelButton.addEventListener("click", closeUpgradePanel);
  upgradePanelDiv.appendChild(cancelButton);

  upgradePanelDiv.style.display = "block";
}


function closeUpgradePanel() {
  upgradePanelDiv.style.display = "none";
}

function handleUpgrade(item) {
  closeUpgradePanel();
  const data = {
        status: 'sent',
        "username": username,
        "item": item.name,
        "itemId": item.id,
    };
  fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'upgrade',
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
        message = responseData.message;
        if (message == "Armor upgraded") {
            alert(`Upgraded ${item.name} to level ${item.armorLevel.current_level + 1}!`);
            location.reload(true);
            blackSmithText.textContent = getRandomMessage('upgradeEquipmentDialogue')
        } else if (message == "Weapon upgraded") {
            alert(`Upgraded ${item.name} to level ${item.weaponLevel.current_level + 1}!`);
            location.reload(true);
            blackSmithText.textContent = getRandomMessage('upgradeEquipmentDialogue')
        } else {
            alert(responseData.message);
        }
    })
}