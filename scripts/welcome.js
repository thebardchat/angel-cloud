// Real-time preview updates
function updatePreview() {
    const worldName = document.getElementById('worldName').value || 'Your Quantum Sanctuary';
    const worldMission = document.getElementById('worldMission').value || 'A digital haven for souls seeking connection and growth...';
    const focusArea = document.getElementById('focusArea').value;
    
    document.getElementById('previewName').textContent = worldName;
    document.getElementById('previewMission').textContent = worldMission;
    
    // Update focus display
    const focusMap = {
        'general': 'General',
        'anxiety': 'Anxiety Relief',
        'depression': 'Depression Support',
        'creativity': 'Creative Expression',
        'relationships': 'Relationships',
        'career': 'Career & Purpose',
        'spiritual': 'Spiritual Growth',
        'teens': 'Teen Support'
    };
    document.getElementById('previewFocus').textContent = focusMap[focusArea] || 'General';
    
    // Update AI blend description
    const empathy = parseInt(document.getElementById('empathy').value);
    const wisdom = parseInt(document.getElementById('wisdom').value);
    const playfulness = parseInt(document.getElementById('playfulness').value);
    const directness = parseInt(document.getElementById('directness').value);
    
    let blendType = 'Balanced';
    if (empathy > 80 && wisdom > 80) blendType = 'Wise Guardian';
    else if (playfulness > 80) blendType = 'Joyful Guide';
    else if (directness > 80) blendType = 'Direct Mentor';
    else if (empathy > 80) blendType = 'Gentle Healer';
    
    document.getElementById('previewBlend').textContent = blendType;
}

// Color palette selection
document.querySelectorAll('.palette-option').forEach(option => {
    option.addEventListener('click', function() {
        document.querySelectorAll('.palette-option').forEach(opt => opt.classList.remove('selected'));
        this.classList.add('selected');
        
        // Update preview colors based on selection
        const palette = this.dataset.palette;
        const preview = document.getElementById('worldPreview');
        
        const colorMap = {
            'classic': '#00ff41',
            'ocean': '#0066ff',
            'sunset': '#ff6600',
            'lavender': '#8040ff'
        };
        
        preview.style.borderColor = colorMap[palette];
        preview.style.boxShadow = `0 0 15px ${colorMap[palette]}40`;
    });
});

// Slider updates
document.querySelectorAll('input[type="range"]').forEach(slider => {
    slider.addEventListener('input', function() {
        const valueDisplay = this.parentNode.querySelector('.slider-value');
        valueDisplay.textContent = this.value + '%';
        updatePreview();
    });
});

// Real-time input updates
document.getElementById('worldName').addEventListener('input', updatePreview);
document.getElementById('worldMission').addEventListener('input', updatePreview);
document.getElementById('focusArea').addEventListener('change', updatePreview);

// Submit for approval function
function submitForApproval() {
    const statusIndicator = document.getElementById('statusIndicator');
    const filterMessage = document.getElementById('filterMessage');
    
    // Simulate submission process
    statusIndicator.className = 'status-indicator status-pending';
    filterMessage.textContent = 'Submitting to Home Base for review...';
    
    setTimeout(() => {
        filterMessage.textContent = 'Under review by Core Values Filter...';
    }, 1500);
    
    setTimeout(() => {
        statusIndicator.className = 'status-indicator status-approved';
        filterMessage.textContent = '✅ Approved! Your world is being built...';
        
        // Show success message
        setTimeout(() => {
            alert('🎉 Congratulations!\n\nYour world "' + (document.getElementById('worldName').value || 'Your Quantum Sanctuary') + '" has been approved!\n\n🌍 Building your personalized Angel Cloud branch...\n💰 +50 Halos awarded for world creation\n🔗 You can now invite others to your world');
        }, 1000);
    }, 4000);
}

// Initialize
updatePreview();
