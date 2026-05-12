/* Funciones comunes de Chart.js */

function createLineChart(canvasId, labels, datasets, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets.map(d => ({
                label: d.label,
                data: d.data,
                borderColor: d.color || '#6c63ff',
                backgroundColor: d.color || '#6c63ff',
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.1,
                fill: false
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: { display: !!title, text: title }
            },
            scales: {
                x: { ticks: { maxTicksLimit: 10 } },
                y: { beginAtZero: false }
            }
        }
    });
}

function createBarChart(canvasId, labels, data, label, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label || 'Valor',
                data: data,
                backgroundColor: color || '#6c63ff',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' });
}

function showError(containerId, message) {
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = `<div class="card"><p class="text-muted">${message}</p></div>`;
}

function setLoading(containerId, loading) {
    const el = document.getElementById(containerId);
    if (el) {
        if (loading) el.classList.add('loading');
        else el.classList.remove('loading');
    }
}
