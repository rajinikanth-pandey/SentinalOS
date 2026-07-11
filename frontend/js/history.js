// js/history.js
const API_URL = 'http://localhost:8000';
let currentPage = 0;
const limit = 20;

document.addEventListener('DOMContentLoaded', function() {
    loadHistory(0);
    
    // Check for log ID in URL
    const urlParams = new URLSearchParams(window.location.search);
    const logId = urlParams.get('log');
    if (logId) {
        loadLogDetail(logId);
    }
});

async function loadHistory(page = 0) {
    currentPage = page;
    const filterMode = document.getElementById('filterMode').value;
    const filterDecision = document.getElementById('filterDecision').value;
    
    let url = `${API_URL}/history?limit=${limit}&offset=${page * limit}`;
    if (filterMode) url += `&mode=${filterMode}`;
    if (filterDecision) url += `&decision=${filterDecision}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        const tbody = document.getElementById('historyTableBody');
        
        if (!data.logs || data.logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No history found</td></tr>';
            return;
        }
        
        let html = '';
        const startIndex = page * limit + 1;
        data.logs.forEach((log, index) => {
            const decision = log.decision || 'UNKNOWN';
            const risk = log.risk_score || 0;
            const mode = log.mode || 'unknown';
            const prompt = log.prompt || '';
            
            let badgeClass = 'badge-warning';
            if (decision === 'BLOCK') badgeClass = 'badge-danger';
            else if (decision === 'ALLOW') badgeClass = 'badge-success';
            
            html += `
                <tr>
                    <td>${startIndex + index}</td>
                    <td>${formatTime(log.timestamp)}</td>
                    <td class="prompt-cell">${escapeHtml(prompt).substring(0, 60)}${prompt.length > 60 ? '...' : ''}</td>
                    <td><span class="badge ${badgeClass}">${decision}</span></td>
                    <td>${risk}/100</td>
                    <td><span class="badge badge-info">${mode}</span></td>
                    <td>
                        <button onclick="viewDetail('${log.log_id}')" class="btn-primary" style="padding:4px 12px;font-size:12px;">
                            🔍 View
                        </button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        
        // Update pagination
        document.getElementById('pageInfo').textContent = `Page ${page + 1}`;
        document.getElementById('prevPage').disabled = page === 0;
        document.getElementById('nextPage').disabled = data.logs.length < limit;
        
    } catch (error) {
        console.error('Error loading history:', error);
        document.getElementById('historyTableBody').innerHTML = '<tr><td colspan="7" class="loading">Error loading history</td></tr>';
    }
}

async function viewDetail(logId) {
    try {
        const response = await fetch(`${API_URL}/history/${logId}`);
        const data = await response.json();
        
        const modal = document.getElementById('detailModal');
        const body = document.getElementById('modalBody');
        
        let html = `
            <h3>📋 Log Details</h3>
            <div style="margin-top:16px;">
                <p><strong>ID:</strong> ${data.log_id}</p>
                <p><strong>Timestamp:</strong> ${formatTime(data.timestamp)}</p>
                <p><strong>Prompt:</strong> ${escapeHtml(data.prompt)}</p>
                <p><strong>Decision:</strong> ${data.decision}</p>
                <p><strong>Risk Score:</strong> ${data.risk_score}/100</p>
                <p><strong>Confidence:</strong> ${data.confidence}</p>
                <p><strong>Mode:</strong> ${data.mode}</p>
                <p><strong>Environment:</strong> ${data.environment}</p>
                <p><strong>Sensitivity:</strong> ${data.sensitivity}</p>
                <p><strong>Action:</strong> ${data.action}</p>
                <p><strong>Tool:</strong> ${data.tool}</p>
                ${data.chat_response ? `<p><strong>Response:</strong> ${escapeHtml(data.chat_response)}</p>` : ''}
            </div>
        `;
        
        body.innerHTML = html;
        modal.style.display = 'flex';
        
    } catch (error) {
        console.error('Error loading log detail:', error);
        alert('Error loading log detail');
    }
}

function loadLogDetail(logId) {
    setTimeout(() => viewDetail(logId), 500);
}

function closeModal() {
    document.getElementById('detailModal').style.display = 'none';
}

async function clearHistory() {
    if (!confirm('⚠️ Are you sure you want to clear all history? This cannot be undone!')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/history?confirm=true`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('History cleared successfully');
            loadHistory(0);
        } else {
            const data = await response.json();
            alert(`Error: ${data.error || 'Failed to clear history'}`);
        }
    } catch (error) {
        console.error('Error clearing history:', error);
        alert('Error clearing history');
    }
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

// Close modal on outside click
document.addEventListener('click', function(event) {
    const modal = document.getElementById('detailModal');
    if (modal && event.target === modal) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});