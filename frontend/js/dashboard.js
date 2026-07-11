// js/dashboard.js
const API_URL = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadRecentActivity();
});

async function loadDashboard() {
    try {
        // Load analytics for all stats
        const analyticsResponse = await fetch(`${API_URL}/analytics`);
        const analytics = await analyticsResponse.json();
        
        console.log('Analytics data:', analytics);
        
        // Update stats with proper fallbacks
       const decisions = analytics.database_stats?.decision_distribution || {};

    document.getElementById('totalRequests').textContent = analytics.total_requests || 0;
    document.getElementById('allowedRequests').textContent = decisions.ALLOW || 0;
    document.getElementById('blockedRequests').textContent = decisions.BLOCK || 0;
    document.getElementById('reviewRequests').textContent = decisions.REVIEW || 0;
    document.getElementById('avgRisk').textContent =
        analytics.database_stats?.average_risk_score || analytics.average_risk || 0;
    document.getElementById('criticalEvents').textContent = analytics.critical_events || 0;
            
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch(`${API_URL}/history?limit=10`);
        const data = await response.json();
        
        const container = document.getElementById('activityList');
        
        if (!data.logs || data.logs.length === 0) {
            container.innerHTML = '<div class="loading">No recent activity</div>';
            return;
        }
        
        let html = '';
        data.logs.forEach(log => {
            const decision = log.decision || 'UNKNOWN';
            const risk = log.risk_score || 0;
            const mode = log.mode || 'unknown';
            const prompt = log.prompt || '';
            
            let badgeClass = 'badge-warning';
            if (decision === 'BLOCK') badgeClass = 'badge-danger';
            else if (decision === 'ALLOW') badgeClass = 'badge-success';
            
            html += `
                <div class="activity-item" onclick="showDetail('${log.log_id}')">
                    <div class="activity-info">
                        <span class="activity-prompt">${escapeHtml(prompt.substring(0, 60))}${prompt.length > 60 ? '...' : ''}</span>
                        <div class="activity-meta">
                            <span class="badge ${badgeClass}">${decision}</span>
                            <span class="risk-badge">Risk: ${risk}/100</span>
                            <span class="mode-badge">${mode}</span>
                            <span class="timestamp">${formatTime(log.timestamp)}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading activity:', error);
        document.getElementById('activityList').innerHTML = '<div class="loading">Error loading activity</div>';
    }
}

function showDetail(logId) {
    window.location.href = `history.html?log=${logId}`;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    try {
        const date = new Date(timestamp);
        return date.toLocaleString();
    } catch {
        return timestamp;
    }
}

function showError(message) {
    // Could implement toast notifications here
    console.error(message);
}