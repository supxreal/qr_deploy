const API_BASE = 'https://qr-deploy-server.onrender.com/api';
// load data when the page is ready
document.addEventListener('DOMContentLoaded', loadData);

// handle form submission
document.getElementById('dataForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // prevent page reload

    const submitBtn = document.querySelector('.btn-submit');
    submitBtn.textContent = 'Generating...';
    submitBtn.disabled = true;

    const payload = {
        username: document.getElementById('username').value,
        description: document.getElementById('description').value,
        link: document.getElementById('link').value
    };

    try {
        const response = await fetch(`${API_BASE}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById('dataForm').reset();
            loadData(); // fetch new data and display it
        } else {
            alert('Oops! Something went wrong.');
        }
    } catch (error) {
        alert('Cannot connect to backend! อย่าลืมรัน python app.py');
        console.error(error);
    } finally {
        submitBtn.textContent = 'Generate QR Code';
        submitBtn.disabled = false;
    }
});

// handle clear data button click
document.getElementById('btnClear').addEventListener('click', clearData);

// fetch and display data
async function loadData() {
    const summaryPane = document.getElementById('summaryPane');

    try {
        const response = await fetch(`${API_BASE}/data`);
        const data = await response.json();

        if (data.length === 0) {
            summaryPane.innerHTML = '<div class="no-data">No information yet</div>';
            return;
        }

        // generate HTML for each item
        summaryPane.innerHTML = data.map(item => `
            <div class="data-card">
                <div class="data-info">
                    <h3>${item.username}</h3>
                    <p>${item.description}</p>
                    <a href="${item.link}" target="_blank">${item.link}</a>
                </div>
                <div class="data-qr">
                    <img src="${item.qr_base64}" alt="QR Code">
                </div>
            </div>
        `).join('');

    } catch (error) {
        summaryPane.innerHTML = '<div class="no-data" style="color: #FF3B30;">Cannot connect to Python backend (Port 8000)</div>';
    }
}

// clear all data
async function clearData() {
    if (!confirm('Are you sure you want to clear ALL data?!')) return;

    try {
        await fetch(`${API_BASE}/clear`, { method: 'DELETE' });
        loadData(); // refresh the page to show empty state
    } catch (error) {
        alert('Error clearing data!');
    }
}
