const spellButton = document.getElementById('spellButton');
const skillsButton = document.getElementById('skillsButton');
const backpackButton = document.getElementById('backpackButton');
const spellbook = document.getElementById('spellbook');
const skills = document.getElementById('skills');
const backpack = document.getElementById('backpack');






spellButton.addEventListener("click", () => toggleForm("spell"));
skillsButton.addEventListener("click", () => toggleForm("skills"));
backpackButton.addEventListener("click", () => toggleForm("backpack"));


function toggleForm(formType) {
  if (formType === "spell") {
    spellbook.classList.add("active");
    skills.classList.remove("active");
    spellButton.classList.add("active");
    backpack.classList.remove("active");
  } else if (formType === "skills") {
    skills.classList.add("active");
    spellbook.classList.remove("active");
    skillsButton.classList.add("active");
    backpack.classList.remove("active");
  } else if (formType === "backpack") {
    backpack.classList.add("active");
    spellbook.classList.remove("active");
    backpackButton.classList.add("active");
    skills.classList.remove("active");
  }
}

  // Set the initial form to show (login by default)
//toggleForm("backpack");

