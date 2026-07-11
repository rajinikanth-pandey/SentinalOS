const API_URL = 'http://localhost:8000';
let charts = {};

document.addEventListener('DOMContentLoaded', function () {
    loadAnalytics();
});

async function loadAnalytics() {
    try {
        const statsResponse = await fetch(`${API_URL}/analytics`);
        const stats = await statsResponse.json();

        // Database stats (correct values)
        const dbStats = stats.database_stats || {};
        const decisions = dbStats.decision_distribution || {};

        const allowed = decisions.ALLOW || 0;
        const blocked = decisions.BLOCK || 0;
        const review = decisions.REVIEW || 0;
        const total = allowed + blocked + review;

        // Summary cards
        document.getElementById('totalEvents').textContent = total || stats.total_requests || 0;

        document.getElementById('blockRate').textContent =
            total ? Math.round((blocked / total) * 100) + '%' : '0%';

        document.getElementById('avgRiskScore').textContent =
            dbStats.average_risk_score || stats.average_risk || 0;

        createDecisionChart(stats);
        createDailyChart();
        createActionsChart(stats);
        createEnvironmentChart(stats);

        loadTrends();

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function createDecisionChart(data) {

    const ctx = document.getElementById('decisionChart').getContext('2d');

    const decisions = data.database_stats?.decision_distribution || {};

    const labels = Object.keys(decisions);
    const values = Object.values(decisions);

    const colors = {
        BLOCK: '#EF4444',
        ALLOW: '#10B981',
        REVIEW: '#F59E0B'
    };

    charts.decision = new Chart(ctx, {
        type: 'pie',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: labels.map(l => colors[l] || '#6B7280'),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createDailyChart() {

    const ctx = document.getElementById('dailyChart').getContext('2d');

    fetch(`${API_URL}/analytics/daily?days=7`)
        .then(res => res.json())
        .then(dailyData => {

            const dailyStats = dailyData.daily_stats || {};

            const dates = Object.keys(dailyStats).sort();

            const counts = dates.map(d => dailyStats[d].count || 0);
            const blocked = dates.map(d => dailyStats[d].blocked || 0);
            const allowed = dates.map(d => dailyStats[d].allowed || 0);

            charts.daily = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dates.map(formatDate),
                    datasets: [
                        {
                            label: 'Total',
                            data: counts,
                            backgroundColor: 'rgba(79,70,229,0.6)',
                            borderColor: '#4F46E5',
                            borderWidth: 2
                        },
                        {
                            label: 'Blocked',
                            data: blocked,
                            backgroundColor: 'rgba(239,68,68,0.6)',
                            borderColor: '#EF4444',
                            borderWidth: 2
                        },
                        {
                            label: 'Allowed',
                            data: allowed,
                            backgroundColor: 'rgba(16,185,129,0.6)',
                            borderColor: '#10B981',
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

        })
        .catch(err => console.error(err));
}

function createActionsChart(data) {

    const ctx = document.getElementById('actionsChart').getContext('2d');

    const actions = data.top_actions || [];

    const labels = actions.map(a => Array.isArray(a) ? a[0] : a.action);
    const values = actions.map(a => Array.isArray(a) ? a[1] : a.count);

    const colors = labels.map((_, i) =>
        `hsla(${(i * 45) % 360},70%,50%,0.7)`
    );

    charts.actions = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.7', '1')),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
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

function createEnvironmentChart(data) {

    const ctx = document.getElementById('environmentChart').getContext('2d');

    const environments =
        data.database_stats?.environment_distribution || {};

    const labels = Object.keys(environments);
    const values = Object.values(environments);

    const colors = {
        production: '#EF4444',
        staging: '#F59E0B',
        development: '#10B981',
        test: '#6B7280',
        unknown: '#9CA3AF'
    };

    charts.environment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: labels.map(l => colors[l] || '#6B7280'),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

async function loadTrends() {

    try {

        const response = await fetch(`${API_URL}/analytics/trends`);
        const trends = await response.json();

        const container = document.getElementById('trendsContent');

        if (trends.message) {
            container.innerHTML = `<div class="loading">${trends.message}</div>`;
            return;
        }

        container.innerHTML = `
            <div class="trend-item">
                <div class="label">Period</div>
                <div class="value">${trends.period_days || 30} days</div>
            </div>

            <div class="trend-item">
                <div class="label">Total Events</div>
                <div class="value">${trends.total_events || 0}</div>
            </div>

            <div class="trend-item">
                <div class="label">Block Rate</div>
                <div class="value">${trends.block_rate || 0}%</div>
            </div>

            <div class="trend-item">
                <div class="label">Trending</div>
                <div class="value" style="color:${trends.trending === 'Increasing' ? '#EF4444' : '#10B981'}">
                    ${trends.trending || 'Stable'}
                </div>
            </div>
        `;

    } catch (error) {

        console.error(error);

        document.getElementById('trendsContent').innerHTML =
            '<div class="loading">Error loading trends</div>';
    }
}

function formatDate(dateStr) {

    if (!dateStr) return '';

    const parts = dateStr.split('-');

    return `${parts[1]}/${parts[2]}`;
}