document.querySelectorAll('.bug-title').forEach(title => {
      title.addEventListener('click', () => {
        const details = title.nextElementSibling;
        const isActive = details.classList.contains('active');

        document.querySelectorAll('.bug-details').forEach(detail => {
          detail.classList.remove('active');
          detail.previousElementSibling.classList.remove('active');
        });

        if (!isActive) {
          details.classList.add('active');
          title.classList.add('active');
        }
      });
    });