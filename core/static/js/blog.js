document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll('.ancorButton');
    const search = document.getElementById('search');
    const funny = document.getElementById('funny');

    funny.addEventListener('click', function(event){
        alert("Pineapple on pizza is bad!");
    })




    buttons.forEach(button => {
      button.addEventListener('click', () => {
      const tag = button.dataset.tag;
      filterBlogs(tag);
      })
    })

    const articles = document.querySelectorAll('article');
    search.addEventListener('input', function(event){
        let value = event.target.value.toLowerCase();
        articles.forEach(article => {
            let title = article.dataset.title.toLowerCase();
            if (title.includes(value)) {
            article.style.display = ''; // show
            } else {
                article.style.display = 'none'; // hide
            }
        })

    })





    window.filterBlogs = function(tag) {
      const articles = document.querySelectorAll('article');
      articles.forEach(article => {
        if (tag === 'all' || article.dataset.tag === tag) {
          article.style.display = 'block';
        } else {
          article.style.display = 'none';
        }
      });
    };

    filterBlogs("all")


})