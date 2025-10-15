// Initialize the map
const map = L.map('map').setView([51.505, -0.09], 5); // Default view over Europe

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Load GeoJSON data
fetch('/static/data/countries.geojson') // Adjust the path if necessary
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            onEachFeature: (feature, layer) => {
                layer.on('click', () => {
                    const countryName = feature.properties.name; // Assuming GeoJSON has a 'name' property
                    document.getElementById('selected-country').value = countryName;
                });
            }
        }).addTo(map);
    });

// Handle form submission
document.getElementById('data-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const country = document.getElementById('selected-country').value;
    const variable = document.getElementById('variable').value;
    const method = document.getElementById('method').value;

    const response = await fetch('/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ country, variable, method })
    });

    const result = await response.json();
    const resultDiv = document.getElementById('result');

    if (response.ok) {
        resultDiv.innerHTML = `<p>Data processed successfully! <a href="${result.download_link}">Download here</a>.</p>`;
    } else {
        resultDiv.innerHTML = `<p>Error: ${result.error}</p>`;
    }
});
