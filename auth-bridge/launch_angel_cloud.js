// ANGEL CLOUD ECOSYSTEM LAUNCHER
// Launches the core three services simultaneously for full system testing.

const { spawn } = require('child_process');

function startService(name, scriptName, port) {
    const process = spawn('node', [scriptName], { stdio: 'inherit' });
    
    process.on('error', (err) => {
        console.error(`[${name} ERROR] Failed to start: ${err.message}`);
    });

    console.log(`\n======================================================`);
    console.log(`🚀 LAUNCHING: ${name}`);
    console.log(`🔗 Access Point: http://localhost:${port}`);
    console.log(`======================================================`);

    return process;
}

// Ensure the Authentication Bridge starts first
const authBridge = startService(
    '1. AUTHENTICATION BRIDGE (SSO)', 
    'angel-auth-bridge.js', 
    3005
);

// Start the Legacy AI (Shanebrain) console interface
const legacyAI = startService(
    '2. LEGACY AI (SHANEBRAIN)', 
    'angel_chat_v2.js', 
    'N/A - Console Only'
);

// Start the Voice Mode interface (Placeholder/Requires microphone setup)
// NOTE: This service runs in its own console/terminal window
const voiceMode = startService(
    '3. VOICE MODE', 
    'voice_mode_final.js', 
    'N/A - Console Only'
);

console.log("\n*** Angel Cloud Ecosystem is fully active. ***\n");