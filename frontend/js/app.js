// js/app.js
const API_URL = 'http://localhost:8000';
let currentReport = null;  // STEP 1: Add global variable

// Send prompt when Enter is pressed (Shift+Enter for new line)
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendPrompt();
    }
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('promptInput');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
});

async function sendPrompt() {
    const input = document.getElementById('promptInput');
    const sendButton = document.getElementById('sendButton');
    const prompt = input.value.trim();
    
    if (!prompt) return;
    
    // Disable input and show loading
    input.disabled = true;
    sendButton.disabled = true;
    sendButton.innerHTML = '⏳';
    
    // Add user message
    addMessage('user', prompt);
    input.value = '';
    input.style.height = 'auto';
    
    // Show thinking indicator
    const thinkingId = addThinkingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt })
        });
        
        // Remove thinking indicator
        removeThinkingIndicator(thinkingId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.mode === 'chat') {
            // Safe request - show AI response
            addMessage('assistant', data.chat.response);
        } else {
            // Blocked request - show security report
            addSecurityMessage(data);
        }
        
    } catch (error) {
        removeThinkingIndicator(thinkingId);
        addMessage('error', `Error: ${error.message}`);
    } finally {
        // Re-enable input
        input.disabled = false;
        sendButton.disabled = false;
        sendButton.innerHTML = '➤';
        input.focus();
    }
}

function addMessage(type, content) {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    if (type === 'user') {
        messageDiv.innerHTML = `<strong>You</strong><br>${escapeHtml(content)}`;
    } else if (type === 'assistant') {
        const formatted = formatResponse(content);
        messageDiv.innerHTML = `<strong>SentinelOS</strong><br>${formatted}`;
    } else if (type === 'error') {
        messageDiv.innerHTML = `<strong>❌ Error</strong><br>${escapeHtml(content)}`;
    }
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addSecurityMessage(data) {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-security';
    
    const analysis = data.analysis || {};
    const risk = analysis.overall_risk || 0;
    const decision = analysis.final_decision || 'BLOCK';
    
    // STEP 2: Store report globally instead of creating JSON string
    currentReport = data;
    
    let html = `
        <div class="security-header">
            <span>🚫 Request Blocked</span>
            <span class="badge badge-danger">${decision}</span>
            <span class="badge badge-danger">Risk: ${risk}/100</span>
        </div>
        <div class="security-details">
            <p><strong>Reason:</strong> ${escapeHtml(data.block_reason || 'Security policy violation')}</p>
    `;
    
    if (data.suggestions && data.suggestions.length > 0) {
        html += `<p><strong>Suggestions:</strong></p><ul>`;
        data.suggestions.forEach(s => {
            html += `<li>${escapeHtml(s)}</li>`;
        });
        html += `</ul>`;
    }
    
    // Add security report details
    const report = data.security_report || {};
    if (report.event) {
        html += `
            <p><strong>Event:</strong> ${escapeHtml(report.event.action || 'unknown')}</p>
            <p><strong>Environment:</strong> ${escapeHtml(report.event.environment || 'unknown')}</p>
            <p><strong>Sensitivity:</strong> ${escapeHtml(report.event.sensitivity || 'unknown')}</p>
        `;
    }
    
    // STEP 3: Remove dataJson parameter from button onclick
    html += `
            <button onclick="viewFullReport()" class="btn-primary" style="margin-top:12px;">
                🔍 View Full Report
            </button>
        </div>
    `;
    
    messageDiv.innerHTML = html;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addThinkingIndicator() {
    const container = document.getElementById('chatMessages');
    if (!container) return null;
    
    const id = 'thinking-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message message-assistant';
    div.innerHTML = '🤔 Thinking<span class="dots">...</span>';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeThinkingIndicator(id) {
    if (!id) return;
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function formatResponse(text) {
    if (!text) return '';
    
    let formatted = escapeHtml(text);
    
    // Code blocks
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code>${escapeHtml(code)}</code></pre>`;
    });
    
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // New lines
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== REPORT MODAL FUNCTIONS ====================

// STEP 4: Replace viewFullReport with simplified version
function viewFullReport() {
    console.log("View Report clicked");

    if (!currentReport) {
        alert("No report found.");
        return;
    }

    const modal = document.getElementById("reportModal");
    const content = document.getElementById("reportContent");

    if (!modal || !content) {
        alert("Modal not found.");
        return;
    }

    content.innerHTML = generateReportHTML(currentReport);
    modal.style.display = "flex";
}

function generateReportHTML(report) {
    const analysis = report.analysis || {};
    const securityReport = report.security_report || {};
    const event = securityReport.event || {};
    const ruleResult = securityReport.rule_result || {};
    const policyResult = securityReport.policy_result || {};
    const agentResults = securityReport.agent_results || [];
    
    const risk = analysis.overall_risk || 0;
    let riskClass = 'score-low';
    if (risk >= 80) riskClass = 'score-high';
    else if (risk >= 50) riskClass = 'score-medium';
    
    let html = `
        <div class="report-section">
            <h4>📊 Summary</h4>
            <div class="report-score">
                <div>
                    <div class="score-value ${riskClass}">${risk}/100</div>
                    <div class="score-label">Risk Score</div>
                </div>
                <div>
                    <div class="score-value">${analysis.final_decision || 'UNKNOWN'}</div>
                    <div class="score-label">Decision</div>
                </div>
                <div>
                    <div class="score-value">${Math.round((analysis.confidence || 0) * 100)}%</div>
                    <div class="score-label">Confidence</div>
                </div>
            </div>
            <div class="field">
                <span class="label">Summary:</span>
                <span class="value">${escapeHtml(analysis.summary || 'No summary')}</span>
            </div>
            ${analysis.recommendations && analysis.recommendations.length > 0 ? `
                <div style="margin-top:8px;">
                    <strong>Recommendations:</strong>
                    ${analysis.recommendations.map(r => `<div class="recommendation-item">${escapeHtml(r)}</div>`).join('')}
                </div>
            ` : ''}
        </div>
        
        <div class="report-section">
            <h4>🛡️ Event Details</h4>
            <div class="field">
                <span class="label">Action:</span>
                <span class="value">${escapeHtml(event.action || 'unknown')}</span>
            </div>
            <div class="field">
                <span class="label">Resource:</span>
                <span class="value">${escapeHtml(event.resource || 'unknown')}</span>
            </div>
            <div class="field">
                <span class="label">Tool:</span>
                <span class="value">${escapeHtml(event.tool || 'unknown')}</span>
            </div>
            <div class="field">
                <span class="label">Environment:</span>
                <span class="value">${escapeHtml(event.environment || 'unknown')}</span>
            </div>
            <div class="field">
                <span class="label">Sensitivity:</span>
                <span class="value">${escapeHtml(event.sensitivity || 'unknown')}</span>
            </div>
        </div>
    `;
    
    // Rule Engine Results
    if (ruleResult && Object.keys(ruleResult).length > 0) {
        html += `
            <div class="report-section">
                <h4>⚖️ Rule Engine Results</h4>
                <div class="field">
                    <span class="label">Decision:</span>
                    <span class="value">${escapeHtml(ruleResult.rule_decision || 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Score:</span>
                    <span class="value">${ruleResult.rule_risk_score || 0}/100</span>
                </div>
                ${ruleResult.rule_reasons && ruleResult.rule_reasons.length > 0 ? `
                    <div style="margin-top:8px;">
                        <strong>Reasons:</strong>
                        ${ruleResult.rule_reasons.map(r => `<div class="violation-item">${escapeHtml(r)}</div>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Policy Results
    if (policyResult && Object.keys(policyResult).length > 0) {
        html += `
            <div class="report-section">
                <h4>📜 Policy Results</h4>
                <div class="field">
                    <span class="label">Decision:</span>
                    <span class="value">${escapeHtml(policyResult.policy_decision || 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Score:</span>
                    <span class="value">${policyResult.policy_score || 0}/100</span>
                </div>
                ${policyResult.violations && policyResult.violations.length > 0 ? `
                    <div style="margin-top:8px;">
                        <strong>Violations:</strong>
                        ${policyResult.violations.map(v => `<div class="violation-item">${escapeHtml(v)}</div>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Agent Results
    if (agentResults && agentResults.length > 0) {
        html += `
            <div class="report-section">
                <h4>🤖 Agent Results</h4>
                ${agentResults.map(agent => `
                    <div style="margin:8px 0; padding:8px 12px; background: var(--surface); border-radius:4px; border-left: 3px solid ${agent.decision === 'BLOCK' ? '#EF4444' : agent.decision === 'ALLOW' ? '#10B981' : '#F59E0B'};">
                        <div><strong>${escapeHtml(agent.agent_name || 'Unknown')}</strong></div>
                        <div class="field">
                            <span class="label">Decision:</span>
                            <span class="value">${escapeHtml(agent.decision || 'N/A')}</span>
                        </div>
                        <div class="field">
                            <span class="label">Risk Score:</span>
                            <span class="value">${agent.risk_score || 0}/100</span>
                        </div>
                        ${agent.reason ? `<div class="field"><span class="label">Reason:</span><span class="value">${escapeHtml(agent.reason)}</span></div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Raw JSON toggle
    html += `
        <button class="report-json-toggle" onclick="toggleReportJSON()">📄 Show Raw JSON</button>
        <div class="report-json" id="reportJSON">${escapeHtml(JSON.stringify(report, null, 2))}</div>
    `;
    
    return html;
}

function toggleReportJSON() {
    const element = document.getElementById('reportJSON');
    if (element) {
        element.classList.toggle('visible');
    }
}

function closeReportModal() {
    const modal = document.getElementById('reportModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeReportModal();
    }
});

// Close modal on outside click (global)
document.addEventListener('click', function(event) {
    const modal = document.getElementById('reportModal');
    if (modal && event.target === modal) {
        closeReportModal();
    }
});