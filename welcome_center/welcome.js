// Matrix Background Animation
const canvas = document.getElementById('matrix-bg');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const matrix = "ANGELCLOUDLOGIBOTSHANEBRAIN01";
const fontSize = 14;
const columns = canvas.width / fontSize;

const drops = [];
for (let i = 0; i < columns; i++) {
    drops[i] = 1;
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(10, 14, 26, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#00ff88';
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
        const text = matrix[Math.floor(Math.random() * matrix.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }

        drops[i]++;
    }
}

setInterval(drawMatrix, 50);

// Resize canvas on window resize
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// Contributor Form Functions
function showContributorForm() {
    document.getElementById('contributor-modal').style.display = 'flex';
}

function showLoginForm() {
    // Simplified for now - in production would be separate form
    alert('Contributor login coming soon. Please apply as a contributor first.');
}

function closeModal() {
    document.getElementById('contributor-modal').style.display = 'none';
}

async function submitContributorForm(event) {
    event.preventDefault();

    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        github_url: document.getElementById('github_url').value,
        github_stats: {
            total_stars: parseInt(document.getElementById('github_stars').value),
            public_repos: parseInt(document.getElementById('public_repos').value)
        },
        email_verified: true  // In production, verify this properly
    };

    try {
        const response = await fetch('/api/contributor/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        const resultDiv = document.getElementById('form-result');

        if (response.ok) {
            resultDiv.className = 'success';
            resultDiv.textContent = result.message || 'Application submitted successfully!';
            document.getElementById('contributor-form').reset();

            setTimeout(() => {
                closeModal();
                resultDiv.style.display = 'none';
            }, 3000);
        } else {
            resultDiv.className = 'error';
            resultDiv.textContent = result.error || 'Application failed. Please check criteria.';

            if (result.criteria) {
                const checks = result.criteria.checks;
                let failedChecks = [];

                for (const [key, check] of Object.entries(checks)) {
                    if (!check.passed) {
                        failedChecks.push(`${key}: Required ${check.required}, got ${check.actual}`);
                    }
                }

                if (failedChecks.length > 0) {
                    resultDiv.textContent += '\n\nFailed checks:\n' + failedChecks.join('\n');
                }
            }
        }
    } catch (error) {
        const resultDiv = document.getElementById('form-result');
        resultDiv.className = 'error';
        resultDiv.textContent = 'Network error. Please try again later.';
        console.error('Error:', error);
    }
}

// Load Live Metrics
async function loadMetrics() {
    try {
        // In production, these would be real API calls
        // For now, simulate with placeholder data

        // Update contributor count
        const contributorsResponse = await fetch('/api/contributions');
        if (contributorsResponse.ok) {
            const data = await contributorsResponse.json();
            document.getElementById('contributors').textContent = data.contributions ? data.contributions.length : '0';
        }

        // Simulate other metrics (would come from backend)
        document.getElementById('total-syncs').textContent = Math.floor(Math.random() * 1000 + 500);
        document.getElementById('ai-queries').textContent = Math.floor(Math.random() * 5000 + 1000);

        // Model count (would query Ollama)
        try {
            const ollamaResponse = await fetch('http://localhost:11434/api/tags');
            if (ollamaResponse.ok) {
                const ollamaData = await ollamaResponse.json();
                const legacyAIModels = ollamaData.models.filter(m => m.name.includes('legacy-ai'));
                document.getElementById('model-count').textContent = legacyAIModels.length;
            }
        } catch (e) {
            document.getElementById('model-count').textContent = '--';
        }

    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

// Status indicator animation
function updateStatus() {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');

    // Check system health
    fetch('/health')
        .then(response => {
            if (response.ok) {
                indicator.style.background = '#00ff88';
                statusText.textContent = 'System Online';
            } else {
                indicator.style.background = '#ffaa00';
                statusText.textContent = 'System Warning';
            }
        })
        .catch(() => {
            indicator.style.background = '#ff0000';
            statusText.textContent = 'System Offline';
        });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadMetrics();
    updateStatus();

    // Refresh metrics every 30 seconds
    setInterval(loadMetrics, 30000);
    setInterval(updateStatus, 10000);
});

// Close modal on outside click
window.addEventListener('click', (event) => {
    const modal = document.getElementById('contributor-modal');
    if (event.target === modal) {
        closeModal();
    }
});
