const deleteButton = document.querySelectorAll(".subButton");
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const username = document.querySelector('meta[name="username"]').content;
const url = '/dashboard/${username}/task/view';



deleteButton.forEach(button => {
    button.addEventListener('click', (e) => {
        const id = button.id;
        const data = {
            status: 'sent',
            id: id,
        };
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Custom-Message': 'delete',
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
            console.log(responseData);
            alert("Task removed");
            const row = button.closest('tr');
            row.remove();
        })
    })
})