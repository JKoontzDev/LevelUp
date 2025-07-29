window.addEventListener('DOMContentLoaded', () => {
  const fill = document.getElementById('fillExp');
  const target = fill.dataset.exp;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const fireButton = document.getElementById('fireButton');
  // Add a short delay to trigger the transition cleanly



  fireButton.addEventListener('click', () => {
  fetch('/fuel/my/fire/')
    .then(res => {
      if (!res.ok) {
        throw new Error(`Server error ${res.status}: ${res.statusText}`);
      }
      return res.json();
    })
    .then(data => {
      alert(data.quote);
    })
    .catch(err => {
      console.error('Fetch failed:', err);
      alert('Oops—couldn’t get your fire. Try again in a bit.');
    });
});





  setTimeout(() => {
    fill.style.width = target + '%';
  }, 100);

});