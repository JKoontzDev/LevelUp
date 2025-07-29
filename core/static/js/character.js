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






spellButton.addEventListener("click", () => toggleForm("spell"));
skillsButton.addEventListener("click", () => toggleForm("skills"));
backpackButton.addEventListener("click", () => toggleForm("backpack"));
weaponsButton.addEventListener("click", () => toggleForm("weapons"));
armorButton.addEventListener("click", () => toggleForm("armors"));


function toggleForm(formType) {
  if (formType === "spell") {
    spellbook.classList.add("active");
    skills.classList.remove("active");
    spellButton.classList.add("active");
    backpack.classList.remove("active");
    weapons.classList.remove("active");
    armors.classList.remove("active")
    document.querySelectorAll('#spellbook li').forEach(function(li) {
        li.addEventListener('click', function() {
          alert(this.dataset.description);
        });
      });

  } else if (formType === "skills") {
    skills.classList.add("active");
    spellbook.classList.remove("active");
    skillsButton.classList.add("active");
    backpack.classList.remove("active");
    weapons.classList.remove("active");
    armors.classList.remove("active")
    document.querySelectorAll('#skills li').forEach(function(li) {
        li.addEventListener('click', function() {
          alert(this.dataset.description);
        });
      });

  } else if (formType === "backpack") {
    backpack.classList.add("active");
    spellbook.classList.remove("active");
    backpackButton.classList.add("active");
    skills.classList.remove("active");
    weapons.classList.remove("active");
    armors.classList.remove("active")
    document.querySelectorAll('#backpack .itemList li').forEach(function(li) {
        li.addEventListener('click', function() {
          alert(this.dataset.description);
        });
      });

  } else if (formType === "armors") {
    backpack.classList.remove("active");
    spellbook.classList.remove("active");
    skills.classList.remove("active");
    armors.classList.add("active")
    weapons.classList.remove("active");
    document.querySelectorAll('#armors .itemList li').forEach(function(li) {
        li.addEventListener('click', function() {
          alert(this.dataset.description);
        });
      });


  }else if (formType === "weapons") {
    backpack.classList.remove("active");
    spellbook.classList.remove("active");
    weapons.classList.add("active");
    skills.classList.remove("active");
    armors.classList.remove("active")
    document.querySelectorAll('#weapons .itemList li').forEach(function(li) {
        li.addEventListener('click', function() {
          alert(this.dataset.description);
        });
      });

  }
}

  // Set the initial form to show (login by default)
//toggleForm("backpack");

