let currentChart = null;
let providerPresets = {};
let currentSettings = {
    provider: 'gemini',
    api_key: '',
    model_name: '',
    base_url: ''
};

// ==========================================
// Navigation
// ==========================================

function showQuery() {
    document.getElementById('queryView').classList.remove('hidden');
    document.getElementById('settingsView').classList.add('hidden');
    document.getElementById('navQuery').classList.add('active');
    document.getElementById('navSettings').classList.remove('active');
}

function showSettings() {
    document.getElementById('queryView').classList.add('hidden');
    document.getElementById('settingsView').classList.remove('hidden');
    document.getElementById('navQuery').classList.remove('active');
    document.getElementById('navSettings').classList.add('active');
    loadSettingsUI();
}

// ==========================================
// Settings: Load Presets
// ==========================================

async function loadSettingsUI() {
    if (Object.keys(providerPresets).length === 0) {
        try {
            const resp = await fetch('/api/settings');
            const data = await resp.json();
            providerPresets = data.presets;
        } catch (e) {
            console.error('Failed to load provider presets:', e);
        }
    }

    const select = document.getElementById('providerSelect');
    select.innerHTML = '';
    for (const [key, val] of Object.entries(providerPresets)) {
        const opt = document.createElement('option');
        opt.value = key;
        opt.textContent = val.label;
        select.appendChild(opt);
    }

    loadFromStorage();
    select.value = currentSettings.provider;
    updateFields();
}

// ==========================================
// Settings: Switch Provider
// ==========================================

function switchProvider() {
    const provider = document.getElementById('providerSelect').value;
    currentSettings.provider = provider;
    updateFields();
}

function updateFields() {
    const preset = providerPresets[currentSettings.provider] || {};
    const useCustom = currentSettings.provider === 'custom';

    document.getElementById('apiKeyInput').value = currentSettings.api_key || '';

    const modelInput = document.getElementById('modelNameInput');
    modelInput.value = currentSettings.model_name || preset.default_model || '';

    const baseUrlGroup = document.getElementById('baseUrlGroup');
    const baseUrlInput = document.getElementById('baseUrlInput');

    if (currentSettings.provider === 'gemini') {
        baseUrlGroup.style.display = 'none';
        baseUrlInput.value = '';
    } else {
        baseUrlGroup.style.display = 'block';
        baseUrlInput.value = currentSettings.base_url || preset.base_url || '';
    }

    if (useCustom) {
        modelInput.placeholder = 'Enter model name';
        baseUrlInput.placeholder = 'https://api.example.com/v1';
    } else {
        modelInput.placeholder = preset.default_model || '';
        baseUrlInput.placeholder = preset.base_url || '';
    }
}

// ==========================================
// Settings: Save / Load from localStorage
// ==========================================

function saveSettings() {
    currentSettings.provider = document.getElementById('providerSelect').value;
    currentSettings.api_key = document.getElementById('apiKeyInput').value.trim();
    currentSettings.model_name = document.getElementById('modelNameInput').value.trim();
    currentSettings.base_url = document.getElementById('baseUrlInput').value.trim();

    localStorage.setItem('llm_provider', currentSettings.provider);
    localStorage.setItem('llm_api_key', currentSettings.api_key);
    localStorage.setItem('llm_model_name', currentSettings.model_name);
    localStorage.setItem('llm_base_url', currentSettings.base_url);

    const status = document.getElementById('connectionStatus');
    status.className = 'connection-status success';
    status.textContent = 'Settings saved!';
    status.style.display = 'block';
    setTimeout(() => { status.style.display = 'none'; }, 2000);
}

function loadFromStorage() {
    currentSettings.provider = localStorage.getItem('llm_provider') || 'gemini';
    currentSettings.api_key = localStorage.getItem('llm_api_key') || '';
    currentSettings.model_name = localStorage.getItem('llm_model_name') || '';
    currentSettings.base_url = localStorage.getItem('llm_base_url') || '';
}

// ==========================================
// Settings: Test Connection
// ==========================================

async function testConnection() {
    saveSettings();

    const status = document.getElementById('connectionStatus');
    status.className = 'connection-status';
    status.textContent = 'Testing connection...';
    status.style.display = 'block';

    try {
        const resp = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: 'test',
                provider: currentSettings.provider,
                api_key: currentSettings.api_key,
                model_name: currentSettings.model_name,
                base_url: currentSettings.base_url
            })
        });

        const data = await resp.json();

        if (data.error) {
            status.className = 'connection-status error';
            status.textContent = 'Connection failed: ' + data.error;
        } else {
            status.className = 'connection-status success';
            status.textContent = 'Connection successful! Provider is working.';
        }
    } catch (e) {
        status.className = 'connection-status error';
        status.textContent = 'Connection failed: ' + e.message;
    }
}

// ==========================================
// Query
// ==========================================

async function sendQuery() {
    const input = document.getElementById("userQuery");
    const query = input.value.trim();
    if (!query) return;

    loadFromStorage();

    // Reset UI
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("resultsArea").classList.add("hidden");
    document.getElementById("errorMsg").classList.add("hidden");
    document.getElementById("chartContainer").classList.add("hidden");

    // Clear previous results
    document.getElementById("contextList").innerHTML = "";
    document.getElementById("tableHead").innerHTML = "";
    document.getElementById("tableBody").innerHTML = "";
    document.getElementById("sqlOutput").textContent = "";
    document.getElementById("explanation").textContent = "";

    try {
        const response = await fetch("/api/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                provider: currentSettings.provider,
                api_key: currentSettings.api_key,
                model_name: currentSettings.model_name,
                base_url: currentSettings.base_url
            })
        });

        const data = await response.json();

        document.getElementById("loading").classList.add("hidden");
        document.getElementById("resultsArea").classList.remove("hidden");

        // 1. Render Context
        if (data.context) {
            const contextContainer = document.getElementById("contextList");
            data.context.forEach(item => {
                const tag = document.createElement("span");
                tag.className = "tag";
                tag.textContent = item.table;
                contextContainer.appendChild(tag);
            });
        }

        // 2. Render SQL & Explanation
        document.getElementById("sqlOutput").textContent = formatSQL(data.sql) || "Could not generate SQL.";
        document.getElementById("explanation").textContent = data.explanation || "";

        // 3. Render Error if any
        if (data.error) {
            const errEl = document.getElementById("errorMsg");
            errEl.textContent = data.error;
            errEl.classList.remove("hidden");
        }

        // 4. Render Table
        if (data.results && data.results.rows) {
            // Header
            const thead = document.getElementById("tableHead");
            const headerRow = document.createElement("tr");
            data.results.columns.forEach(col => {
                const th = document.createElement("th");
                th.textContent = col;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);

            // Body
            const tbody = document.getElementById("tableBody");
            data.results.rows.forEach(row => {
                const tr = document.createElement("tr");
                row.forEach(cell => {
                    const td = document.createElement("td");
                    td.textContent = cell;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }

        // 5. Render Chart
        if (data.chart_config) {
            renderChart(data.chart_config, data.results);
        }

    } catch (e) {
        document.getElementById("loading").classList.add("hidden");
        const errEl = document.getElementById("errorMsg");
        errEl.textContent = "Network Error: " + e;
        errEl.classList.remove("hidden");
        document.getElementById("resultsArea").classList.remove("hidden");
    }
}

function formatSQL(sql) {
    if (!sql) return null;
    return sql.replace(/\s+/g, " ").trim();
}

function copySql() {
    const text = document.getElementById("sqlOutput").textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.querySelector(".copy-btn");
        const original = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(() => btn.textContent = original, 2000);
    });
}

function renderChart(config, data) {
    const ctx = document.getElementById('dataChart').getContext('2d');
    const chartContainer = document.getElementById('chartContainer');

    // Unhide container
    chartContainer.classList.remove('hidden');

    // Destroy old chart if exists
    if (currentChart) {
        currentChart.destroy();
    }

    // Extract Data using Column Mapping Strategy
    const xColIndex = data.columns.indexOf(config.x_column);
    if (xColIndex === -1) {
        console.warn("X-Column not found.");
        chartContainer.classList.add('hidden');
        return;
    }

    const labels = data.rows.map(row => row[xColIndex]);
    const datasets = [];
    const colors = [
        'rgba(37, 99, 235',   // Blue
        'rgba(220, 38, 38',   // Red
        'rgba(22, 163, 74',   // Green
        'rgba(217, 119, 6',   // Amber
        'rgba(147, 51, 234'   // Purple
    ];

    // Loop through each Y-column to create a dataset
    config.y_columns.forEach((colName, index) => {
        const yColIndex = data.columns.indexOf(colName);
        if (yColIndex !== -1) {
            const values = data.rows.map(row => row[yColIndex]);
            const colorBase = colors[index % colors.length];

            datasets.push({
                label: config.labels[index] || colName,
                data: values,
                backgroundColor: `${colorBase}, 0.5)`,
                borderColor: `${colorBase}, 1)`,
                borderWidth: 1
            });
        }
    });

    if (datasets.length === 0) {
        console.warn("No valid Y-columns found.");
        chartContainer.classList.add('hidden');
        return;
    }

    // Create New Chart
    currentChart = new Chart(ctx, {
        type: config.chart_type,
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: config.title
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Enter Key Support
document.getElementById("userQuery").addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
    }
});
