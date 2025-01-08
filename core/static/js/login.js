document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const loginBtn = document.getElementById("loginBtn");
  const registerBtn = document.getElementById("registerBtn");
  const loginText = document.getElementById("loginText")
  const registerText = document.getElementById("registerText")


  loginBtn.addEventListener("click", () => toggleForm("login"));
  registerBtn.addEventListener("click", () => toggleForm("register"));
  loginText.addEventListener("click", () => toggleForm("login"));
  registerText.addEventListener("click", () => toggleForm("register"));

  function toggleForm(formType) {
    if (formType === "login") {
      loginForm.classList.add("active");
      registerForm.classList.remove("active");
      loginBtn.classList.add("active");
      registerBtn.classList.remove("active");
    } else if (formType === "register") {
      registerForm.classList.add("active");
      loginForm.classList.remove("active");
      registerBtn.classList.add("active");
      loginBtn.classList.remove("active");
    }
  }

  // Set the initial form to show (login by default)
  toggleForm("login");
});