const url = '/dashboard/${username}/market/items';
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const username = document.querySelector('meta[name="username"]').content;
const storedItems = localStorage.getItem('items');
const shopkeeper = document.getElementById('shopkeeperText');



document.addEventListener('DOMContentLoaded', function() {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        const username = document.querySelector('meta[name="username"]').content;
        const itemGrid = document.getElementById('itemGrid');
        const buttons = document.querySelectorAll('.category-btn');
        const currentDate = new Date().toISOString().split('T')[0];
        const storedDate = localStorage.getItem('lastFetchedDate');
        const storedItems = localStorage.getItem('items');

        const data = {
            status: 'completed'
        };
        let items = {
            armor: [],
            weapons: [],
            ingredients: [],
            misc: []
        };


        if (storedItems && storedDate === currentDate) {
            items = JSON.parse(storedItems);
            console.log('Loaded items from localStorage:', items);
            buttons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const category = e.target.dataset.category;
                    displayItems(category, items);
                });
            });
        } else {
                    // If no data or data is outdated, fetch it
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json(); // Parse JSON response
        })
        .then(responseData => {
            if (Array.isArray(responseData)) {
                responseData.forEach(item => {
                    if (item.type == "ingredient") {
                        items.ingredients.push({
                            name: item.item,
                            price: item.price.toFixed(2),
                            description: item.description
                        });
                    } else if (item.type == "armor") {
                        items.armor.push({
                            name: item.item,
                            price: item.price.toFixed(2),
                            description: item.description
                        });
                    } else if (item.type == "weapon") {
                        items.weapons.push({
                            name: item.item,
                            price: item.price.toFixed(2),
                            description: item.description
                        });
                    } else if (item.type == "misc") {
                        items.misc.push({
                            name: item.item,
                            price: item.price.toFixed(2),
                            description: item.description
                        });
                    }
                });
            }

            // Store items and the current date in localStorage
            localStorage.setItem('items', JSON.stringify(items));
            localStorage.setItem('lastFetchedDate', currentDate);

            console.log('Fetched new items:', items);

            // Proceed with displaying the items
            buttons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const category = e.target.dataset.category;
                    displayItems(category, items);
                });
            });
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
    }
});



function displayItems(category, items) {
    itemGrid.innerHTML = ''; // Clear the grid



    if (items[category].length == 0) {
        const itemElement = document.createElement('div');
        itemElement.className = 'item';

        const noItemsText = document.createElement('h3');
        noItemsText.textContent = 'Sorry no items for sale'; // Safe text insertion
        itemElement.appendChild(noItemsText);

        itemGrid.appendChild(itemElement);
    } else {
        items[category].forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'item';

            const itemName = document.createElement('h3');
            itemName.textContent = item.name; // Safe text insertion
            itemElement.appendChild(itemName);

            const itemPrice = document.createElement('p');
            itemPrice.textContent = `Price: ${item.price} gold`;
            itemElement.appendChild(itemPrice);

            const buyBut = document.createElement('button');
            buyBut.textContent = `Buy now`;
            buyBut.id = `${item.name}`;
            buyBut.classList.add('buyButton');
            itemElement.appendChild(buyBut);


            buyBut.addEventListener('click', function () {
                const data = {
                    status: 'sent',
                    itemName: buyBut.id,
                    username: username,
                };
                fetch(url, {
                    method: 'Post',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
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
                    //console.log("BELLOW");
                    //console.log(responseData.message);
                    if (responseData.message == "Task completed successfully!") {
                        const itemNameToRemove = responseData.item
                        //console.log(itemNameToRemove)
                        let items = JSON.parse(localStorage.getItem('items')) || {};
                        for (const category in items) {
                            if (Array.isArray(items[category])) {
                                items[category] = items[category].filter(item => item.name !== itemNameToRemove);
                            }
                        }
                        localStorage.setItem('items', JSON.stringify(items));
                        shopkeeper.textContent = `Thanks for buying ${itemNameToRemove}!`;

                        const divToRemove = document.getElementById(itemNameToRemove);
                        if (divToRemove) {
                            const parentDiv = divToRemove.parentElement;
                            if (parentDiv) {
                                parentDiv.remove();
                                //console.log(`Button and its parent div with ID '${itemNameToRemove}' have been removed.`);
                            }
                        } else {
                            console.log(`Button with ID '${itemNameToRemove}' does not exist.`);
                        }
                    } else {
                        shopkeeper.textContent = "Sorry no free handouts!";

                    }


                })

            });

            itemGrid.appendChild(itemElement);
        });
    }
}