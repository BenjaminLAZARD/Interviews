document.getElementById('search-btn').addEventListener('click', function () {
    performSearch();
});

document.getElementById('query-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        performSearch();
    }
});

function performSearch() {
    const query = document.getElementById('query-input').value;
    if (!query) return;

    fetch(`/query/?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => displayResults(data))
        .catch(error => console.error('Error fetching data:', error));
}

function displayResults(results) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = '';

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No results found.</p>';
        return;
    }

    const table = document.createElement('table');
    const headerRow = table.insertRow();
    ['Title', 'Link', 'Publication Date', 'Creator', 'Source'].forEach(text => {
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
        const toggleCell = row.insertCell();
        const toggleBtn = document.createElement('button');
        toggleBtn.classList.add('toggle-btn');
        toggleBtn.innerHTML = '<span class="triangle"></span>';

        // Create a description row below
        const descriptionRow = table.insertRow();
        const descriptionCell = descriptionRow.insertCell();
        descriptionCell.colSpan = 6;
        const descriptionDiv = document.createElement('div');
        descriptionDiv.classList.add('description');
        descriptionDiv.textContent = article.description;
        descriptionDiv.style.display = 'none'; // Hide by default
        descriptionCell.appendChild(descriptionDiv);

        toggleBtn.addEventListener('click', function () {
            const isVisible = descriptionDiv.style.display === 'block';
            descriptionDiv.style.display = isVisible ? 'none' : 'block';
            toggleBtn.innerHTML = `<span class="triangle ${isVisible ? '' : 'active'}"></span>`;
        });

        toggleCell.appendChild(toggleBtn);
    });

    resultsContainer.appendChild(table);
}
