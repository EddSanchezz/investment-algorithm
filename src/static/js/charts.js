/* Funciones comunes de Chart.js */

const chartRegistry = window.__chartRegistry || {};
window.__chartRegistry = chartRegistry;

function destroyChart(canvasId) {
    const existing = chartRegistry[canvasId] || Chart.getChart(canvasId);
    if (existing) {
        existing.destroy();
        delete chartRegistry[canvasId];
    }
}

function createLineChart(canvasId, labels, datasets, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    destroyChart(canvasId);
    const chart = new Chart(ctx, {
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
                spanGaps: true,
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
    chartRegistry[canvasId] = chart;
    return chart;
}

function createBarChart(canvasId, labels, data, label, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    destroyChart(canvasId);
    const chart = new Chart(ctx, {
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
    chartRegistry[canvasId] = chart;
    return chart;
}

function renderMath(container) {
    if (!container) return Promise.resolve();
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        return window.MathJax.typesetPromise([container]).catch(err => {
            console.error('MathJax typeset error:', err);
        });
    }
    return Promise.resolve();
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
