document.getElementById('search-btn').addEventListener('click', function () {
    const query = document.getElementById('query-input').value;
    if (!query) return;

    fetch(`/query/?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => displayResults(data))
        .catch(error => console.error('Error fetching data:', error));
});

// Adding functionality to hit enter for search
document.getElementById('query-input').addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
        document.getElementById('search-btn').click();
    }
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
    ['Title', 'Link', 'Publication Date', 'Creator', 'Source', 'Toggle'].forEach(text => {
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

        // Create a toggle button
        const toggleButton = document.createElement('button');
        toggleButton.classList.add('toggle-btn');
        toggleButton.innerHTML = '<span class="triangle"></span>'; // Add triangle element
        row.insertCell().appendChild(toggleButton);

        // Create a new row for the description
        const descriptionRow = table.insertRow();
        const descriptionCell = descriptionRow.insertCell();
        descriptionCell.colSpan = 6; // Span across all columns
        descriptionCell.classList.add('description');
        descriptionCell.textContent = article.description;
        descriptionRow.style.display = 'none'; // Hide the description row by default

        toggleButton.addEventListener('click', function () {
            const isVisible = descriptionRow.style.display === 'table-row';
            descriptionRow.style.display = isVisible ? 'none' : 'table-row';
            this.classList.toggle('active', !isVisible); // Toggle active class on button
        });
    });

    resultsContainer.appendChild(table);
}
