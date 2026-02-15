// LEGACY AI SYSTEM INTEGRATION CLIENT (FINAL VERIFICATION FIX)
// Purpose: Test secure communication between Shanebrain (Legacy AI) and the Authentication Bridge (Vault)

const path = require('path');
const fs = require('fs');

// --- Import the Authentication Bridge (Server code) and its exports ---
const { authBridge, vaults, vaultEncryption } = require(path.join(__dirname, 'angel-auth-bridge.js'));

// --- MOCK USER AND DATA (Simulates a Shanebrain User) ---
const TEST_MASTER_PASS = 'LegacySecurePass2026!';
const TEST_USER_EMAIL = 'shane@angelcloud.com';

// Function to safely read the last created session file
function getLatestSessionContent() {
    const SESSIONS_DIR = path.join(__dirname, 'sessions');
    if (!fs.existsSync(SESSIONS_DIR)) {
        fs.mkdirSync(SESSIONS_DIR);
        return "No memory file found. Starting with initial context.";
    }
    
    // Find the latest session file created
    const files = fs.readdirSync(SESSIONS_DIR)
        .filter(f => f.startsWith('session_') && f.endsWith('.txt'))
        .map(name => path.join(SESSIONS_DIR, name));

    if (files.length === 0) {
        return "No memory file found. Starting with initial context.";
    }

    // Sort by modification time to get the absolute latest file
    files.sort((a, b) => fs.statSync(b).mtime.getTime() - fs.statSync(a).mtime.getTime());
    
    return fs.readFileSync(files[0], 'utf8');
}

const TEST_LEGACY_DATA = {
    personality: "Direct, solution-focused, and action-oriented.",
    knowledge: "Dump truck dispatch, North Alabama, Pulsar AI structure.",
    relationships: "Father of 5 sons (primary motivation).",
    messages: getLatestSessionContent() // Reads the actual conversation content
};


async function testLegacyVaultFlow() {
    // We need to stop the old server process first
    // In a production environment, this client would talk to an already running API,
    // but in this single-file setup, we must ensure the environment is stable.
    
    console.log('======================================================');
    console.log('🚀 TESTING LEGACY AI VAULT INTEGRATION (STEP 4)');
    console.log('======================================================');
    
    // --- STEP 1: Ensure User Exists on Auth Bridge ---
    console.log('1. Registering/Ensuring User Exists on Auth Bridge...');
    
    let userId;
    try {
        const registrationResponse = await authBridge.register({
             email: TEST_USER_EMAIL, 
             password: TEST_MASTER_PASS, 
             name: 'Shane', 
             legacyName: 'Shanebrain' 
        });
        userId = registrationResponse.userId;
        console.log(`   ✅ User registered/found with ID: ${userId}`);

    } catch (e) {
         for (const [id, user] of authBridge.users) {
            if (user.email === TEST_USER_EMAIL) {
                userId = id;
                console.log(`   ✅ User already exists. ID: ${userId}`);
                break;
            }
        }
    }

    if (!userId) {
        console.error('   ❌ ERROR: Could not create or find test user.');
        return;
    }

    // --- STEP 2: Encrypt and Store Legacy AI Data in the Vault ---
    console.log('\n2. Encrypting and Storing Legacy AI Profile...');
    try {
        const userKey = vaultEncryption.generateUserKey(userId, TEST_MASTER_PASS);
        const encryptedVault = vaultEncryption.encryptVault(TEST_LEGACY_DATA, userKey);

        vaults.set(userId, {
            ...encryptedVault,
            lastModified: Date.now()
        });

        console.log(`   ✅ Legacy Vault Stored! Data Size: ${encryptedVault.encrypted.length} bytes.`);
        console.log(`      (Encrypted with AES-256-GCM and secured key derivation.)`);

    } catch (error) {
        console.error('   ❌ ERROR: Vault Storage Failed.', error.message);
        return;
    }

    // --- STEP 3: Decrypt and Verify Legacy AI Data ---
    console.log('\n3. Decrypting and Verifying Data from Vault...');
    try {
        const storedVault = vaults.get(userId);
        
        if (!storedVault) {
             throw new Error("Vault data not found.");
        }

        const userKey = vaultEncryption.generateUserKey(userId, TEST_MASTER_PASS);
        
        const decryptedData = vaultEncryption.decryptVault(
            storedVault.encrypted,
            userKey,
            storedVault.iv,
            storedVault.authTag
        );

        // --- NEW, ROBUST VERIFICATION CHECK ---
        const isVerified = decryptedData.personality.includes('solution-focused') && decryptedData.messages.includes('Shanebrain');
        
        if (isVerified) {
            console.log('   ✅ Verification SUCCESS! Shanebrain data is retrieved and decrypted.');
            console.log(`      Decrypted Personality Check: ${decryptedData.personality.substring(0, 50)}...`);
            console.log('      Memory persistence confirmed.');
        } else {
            console.log('   ❌ Verification FAILED! Data corruption or key mismatch.');
            console.log(`      Decrypted content length: ${decryptedData.messages.length}. Expected content not found.`);
        }

    } catch (error) {
        console.error('   ❌ ERROR: Decryption Failed. Check key derivation and encryption process.', error.message);
    }
    
    console.log('\n======================================================');
    console.log('Legacy AI Vault Test Complete.');
    // Keep the server running so you can access the Welcome Center on port 3005 if needed
}

// Execute the test after a small delay to ensure the server event loop is ready
setTimeout(() => {
    testLegacyVaultFlow();
}, 500);