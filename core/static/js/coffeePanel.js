// coffeePanel.js

window.addEventListener("DOMContentLoaded", () => {
  const coffeeLink = document.getElementById("coffeeLink");
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const url = '/collect_email/'
  if (coffeeLink) {
    coffeeLink.addEventListener("click", function (e) {
      e.preventDefault();
      createSidePanel(csrfToken);
      setTimeout(() => {
        window.open(this.href, '_blank');
      }, 500);
    });
  }
});

function createSidePanel(csrfToken) {
  if (document.getElementById('sidePanel')) return; // prevent duplicates

  const panel = document.createElement('div');
  panel.id = 'sidePanel';
  Object.assign(panel.style, {
    position: 'fixed',
    top: '0',
    right: '-400px',
    width: '350px',
    height: '100%',
    background: 'linear-gradient(to bottom, #16213e, #0f3460)',
    boxShadow: '-5px 0 15px rgba(0,0,0,0.3)',
    padding: '25px',
    zIndex: '9999',
    color: 'white',
    fontFamily: "'Segoe UI', sans-serif",
    transition: 'right 0.4s ease',
    borderTopLeftRadius: '20px',
    borderBottomLeftRadius: '20px'
  });

  const title = document.createElement('h2');
  title.textContent = "☕ You're the best!";
  panel.appendChild(title);

  const msg = document.createElement('p');
  msg.style.fontSize = '16px';
  msg.textContent = `Thanks for buying me a coffee! 🎉Enter your email to unlock exclusive content: Note email or name must match email/username associated with levelUp`;
  panel.appendChild(msg);

  const emailInput = document.createElement('input');
  emailInput.type = 'email';
  emailInput.id = 'emailInput';
  emailInput.placeholder = 'you@example.com';
  Object.assign(emailInput.style, {
    width: '94%',
    padding: '10px',
    marginTop: '10px',
    border: 'none',
    borderRadius: '8px',
    boxShadow: 'inset 0 0 5px rgba(0,0,0,0.2)'
  });
  panel.appendChild(emailInput);

  const redeemBtn = document.createElement('button');
  redeemBtn.id = 'redeemBtn';
  redeemBtn.textContent = '🎁 Redeem';
  Object.assign(redeemBtn.style, {
    marginTop: '15px',
    padding: '10px',
    width: '100%',
    background: '#4caf50',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background 0.3s ease'
  });
  redeemBtn.addEventListener('click', () => {
    const email = emailInput.value;
    if (email) {
      fetch('/api/redeem/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ email: emailInput.value })
    })
    .then(res => res.json())
    .then(data => {
      alert("🎉 Thanks! I will update your profile");
      panel.style.right = "-400px";
      setTimeout(() => panel.remove(), 400);
    })
    .catch(err => {
      console.error('Error:', err);
      alert("Oops! Something went wrong.");
    });
      panel.style.right = "-400px";
      setTimeout(() => panel.remove(), 400);
    } else {
      alert("Please enter a valid email.");
    }
  });
  panel.appendChild(redeemBtn);

  const closeBtn = document.createElement('button');
  closeBtn.id = 'closePanel';
  closeBtn.textContent = 'Close';
  Object.assign(closeBtn.style, {
    marginTop: '15px',
    background: 'transparent',
    border: 'none',
    color: 'white',
    cursor: 'pointer',
    textDecoration: 'underline',
    fontSize: '14px'
  });
  closeBtn.addEventListener('click', () => {
    panel.style.right = "-400px";
    setTimeout(() => panel.remove(), 400);
  });
  panel.appendChild(closeBtn);

  document.body.appendChild(panel);

  // Animate in
  requestAnimationFrame(() => {
    panel.style.right = "0";
  });
}
