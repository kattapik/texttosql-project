let currentChart = null;

async function sendQuery() {
    const input = document.getElementById("userQuery");
    const query = input.value.trim();
    if (!query) return;

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
            body: JSON.stringify({ query: query })
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
    const yColIndex = data.columns.indexOf(config.y_column);

    if (xColIndex === -1 || yColIndex === -1) {
        console.warn("Chart columns not found in data result.");
        chartContainer.classList.add('hidden');
        return;
    }

    const labels = data.rows.map(row => row[xColIndex]);
    const values = data.rows.map(row => row[yColIndex]);

    // Create New Chart
    currentChart = new Chart(ctx, {
        type: config.chart_type,
        data: {
            labels: labels,
            datasets: [{
                label: config.label || config.y_column,
                data: values,
                backgroundColor: 'rgba(37, 99, 235, 0.5)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 1
            }]
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
