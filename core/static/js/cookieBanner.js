(function() {
  if (localStorage.getItem('cookieConsent')) {
    return;
  }

  const banner = document.createElement('div');
  banner.id = 'cookie-banner';
  banner.style.position = 'fixed';
  banner.style.bottom = '0';
  banner.style.width = '100%';
  banner.style.backgroundColor = '#000';
  banner.style.color = '#fff';
  banner.style.textAlign = 'center';
  banner.style.padding = '1em 0';
  banner.style.zIndex = '1000';
  banner.style.fontFamily = 'Arial, sans-serif';
  banner.style.fontSize = '14px';

  const message = document.createElement('span');
  message.textContent = 'This site uses essential cookies. By continuing you agree to our use of cookies.';

  const acceptButton = document.createElement('button');
  acceptButton.id = 'accept-cookies';
  acceptButton.textContent = 'Accept';
  acceptButton.style.backgroundColor = '#444';
  acceptButton.style.color = '#fff';
  acceptButton.style.border = 'none';
  acceptButton.style.padding = '0.5em 1em';
  acceptButton.style.marginRight = '0.5em';
  acceptButton.style.cursor = 'pointer';

  const declineButton = document.createElement('button');
  declineButton.id = 'decline-cookies';
  declineButton.textContent = 'Decline';
  declineButton.style.backgroundColor = '#222';
  declineButton.style.color = '#fff';
  declineButton.style.border = 'none';
  declineButton.style.padding = '0.5em 1em';
  declineButton.style.cursor = 'pointer';

  banner.appendChild(message);
  banner.appendChild(acceptButton);
  banner.appendChild(declineButton);

  document.body.appendChild(banner);

  document.getElementById('accept-cookies').addEventListener('click', function() {
    // Store consent in localStorage
    localStorage.setItem('cookieConsent', 'accepted');
    banner.remove();
    // (Optional) Here i can initialize analytics or other scripts in future

  });

  document.getElementById('decline-cookies').addEventListener('click', function() {
    localStorage.setItem('cookieConsent', 'declined');
    banner.remove();
  });
})();
