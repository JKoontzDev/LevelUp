const spellButton = document.getElementById('spellButton');
const skillsButton = document.getElementById('skillsButton');
const backpackButton = document.getElementById('backpackButton');
const armorButton = document.getElementById('armorsButton');
const weaponsButton = document.getElementById('weaponsButton');
const spellbook = document.getElementById('spellbook');
const skills = document.getElementById('skills');
const backpack = document.getElementById('backpack');
const weapons = document.getElementById('weapons');
const armors = document.getElementById('armors');
const username = document.querySelector('meta[name="username"]').content;
const url = `/dashboard/${username}/character/`
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;


function equip(item) {
  const data = { item: item };

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Custom-User': username
    },
    body: JSON.stringify(data),
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok: ' + response.statusText);
    }
    return response.json(); // Parse JSON response
  })
  .then(responseData => {
    alert(responseData.message);
  })
  .catch(error => {
    console.error('Fetch error:', error);
    alert('Something went wrong: ' + error.message);
  });
}


spellButton.addEventListener("click", () => toggleForm("spell"));
skillsButton.addEventListener("click", () => toggleForm("skills"));
backpackButton.addEventListener("click", () => toggleForm("backpack"));
weaponsButton.addEventListener("click", () => toggleForm("weapons"));
armorButton.addEventListener("click", () => toggleForm("armors"));





document.querySelectorAll('.equipItem').forEach(function(button) {
    button.addEventListener('click', function() {
        equip(this.id)
    })
});
document.querySelectorAll('.details').forEach(function(button) {
    button.addEventListener('click', function() {
        alert(this.dataset.description);
    });
});

document.querySelectorAll('#backpack .itemList li').forEach(function(li) {
    li.addEventListener('click', function() {
        alert(this.dataset.description);
    });
});


document.querySelectorAll('#skills li').forEach(function(li) {
    li.addEventListener('click', function() {
        alert(this.dataset.description);
    });
});


document.querySelectorAll('#spellbook li').forEach(function(li) {
    li.addEventListener('click', function() {
        alert(this.dataset.description);
    });
});

function toggleForm(formType) {
  if (formType === "spell") {
    spellbook.classList.add("active");
    skills.classList.remove("active");
    spellButton.classList.add("active");
    backpack.classList.remove("active");
    weapons.classList.remove("active");
    armors.classList.remove("active")


  } else if (formType === "skills") {
    skills.classList.add("active");
    spellbook.classList.remove("active");
    skillsButton.classList.add("active");
    backpack.classList.remove("active");
    weapons.classList.remove("active");
    armors.classList.remove("active")


  } else if (formType === "backpack") {
    backpack.classList.add("active");
    spellbook.classList.remove("active");
    backpackButton.classList.add("active");
    skills.classList.remove("active");
    weapons.classList.remove("active");
    armors.classList.remove("active")


  } else if (formType === "armors") {
    backpack.classList.remove("active");
    spellbook.classList.remove("active");
    skills.classList.remove("active");
    armors.classList.add("active")
    weapons.classList.remove("active");



  }else if (formType === "weapons") {
    backpack.classList.remove("active");
    spellbook.classList.remove("active");
    weapons.classList.add("active");
    skills.classList.remove("active");
    armors.classList.remove("active")

}
}
  // Set the initial form to show (login by default)
//toggleForm("backpack");


