document.getElementById('search-btn').addEventListener('click', function () {
    const query = document.getElementById('query-input').value;
    if (!query) return;

    fetch(`/query/?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => displayResults(data))
        .catch(error => console.error('Error fetching data:', error));
});

function displayResults(results) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = '';

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No results found.</p>';
        return;
    }

    const table = document.createElement('table');
    const headerRow = table.insertRow();
    ['Title', 'Link', 'Publication Date', 'Creator', 'Source', 'Description'].forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });

    results.forEach(article => {
        const row = table.insertRow();
        row.insertCell().textContent = article.title;
        const linkCell = row.insertCell();
        const link = document.createElement('a');
        link.href = article.link;
        link.textContent = 'View';
        link.target = '_blank';
        linkCell.appendChild(link);
        row.insertCell().textContent = article.publication_date;
        row.insertCell().textContent = article.creator;
        row.insertCell().textContent = article.source;

        const descriptionCell = row.insertCell();
        const toggleButton = document.createElement('span');
        toggleButton.classList.add('toggle-description');
        toggleButton.textContent = 'Show';
        toggleButton.addEventListener('click', function () {
            const descriptionDiv = this.nextElementSibling;
            if (descriptionDiv.style.display === 'none') {
                descriptionDiv.style.display = 'block';
                this.textContent = 'Hide';
            } else {
                descriptionDiv.style.display = 'none';
                this.textContent = 'Show';
            }
        });
        descriptionCell.appendChild(toggleButton);

        const descriptionDiv = document.createElement('div');
        descriptionDiv.classList.add('description');
        descriptionDiv.textContent = article.description;
        descriptionCell.appendChild(descriptionDiv);
    });

    resultsContainer.appendChild(table);
}
