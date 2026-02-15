// ANGEL CLOUD AUTHENTICATION BRIDGE (FINAL MVP BUILD)
// Purpose: Unifies Legacy AI, Pulsar Security, SSO, and the Dispatch Calculator.

const express = require('express');
const crypto = require('crypto');
const { ethers } = require('ethers');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');
const rateLimit = require('express-rate-limit'); 
const fs = require('fs'); 
const path = require('path');
const dotenv = require('dotenv'); 

// --- IMPORT CORE SERVICES ---
const PulsarSecurity = require('./pulsar_security_core'); 
const calculateOptimalWindow = require('./dispatch_calculator_service'); // Import the calculator function

const app = express();
app.use(express.json());


// --- ENVIRONMENT CONFIGURATION (ROBUST KEY CHECK) ---
const ENV_FILE = path.join(__dirname, '.env');
dotenv.config({ path: ENV_FILE, override: true }); // Ensure .env is loaded and can override existing env vars

const JWT_SECRET = process.env.JWT_SECRET;
const PULSAR_API_KEY = process.env.PULSAR_API_KEY;
const ENCRYPTION_SECRET_STRING = process.env.ENCRYPTION_SECRET;
const ETHEREUM_NETWORK = process.env.ETHEREUM_NETWORK;


// --- CRITICAL CHECK: ENSURE ENCRYPTION SECRET IS VALID ---
let ENCRYPTION_KEY;
if (!ENCRYPTION_SECRET_STRING || ENCRYPTION_SECRET_STRING.length !== 64) {
    console.error("❌ FATAL: ENCRYPTION_SECRET is missing or invalid in .env. It must be a 32-byte hex string (64 characters).");
    process.exit(1); 
} else {
    try {
        ENCRYPTION_KEY = Buffer.from(ENCRYPTION_SECRET_STRING, 'hex');
    } catch(e) {
        console.error("❌ FATAL: Could not convert ENCRYPTION_SECRET to buffer. Check format.");
        process.exit(1);
    }
}


// --- SECURITY & RATE LIMITING ---
const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 10, 
    message: "Too many login attempts from this IP, please try again after 15 minutes."
});

app.use('/api/auth/sso-login', loginLimiter);
app.use(express.static('public'));


// --- IN-MEMORY STORES (REPLACE WITH DB) ---
const users = new Map();
const vaults = new Map(); 
const biometricTokens = new Map();


// --- ETHERS SETUP & INITIALIZATION ---
const provider = new ethers.providers.JsonRpcProvider(ETHEREUM_NETWORK);
const pulsarCore = new PulsarSecurity();


// --- MIDDLEWARE: VERIFY SSO TOKEN ---
function verifySSO(req, res, next) {
    const token = req.headers['authorization'];
    if (!token) {
        return res.status(403).json({ error: 'Access denied: No SSO token provided.' });
    }
    
    try {
        const payload = jwt.verify(token.replace('Bearer ', ''), JWT_SECRET);
        req.userId = payload.userId;
        next();
    } catch (e) {
        return res.status(401).json({ error: 'Access denied: Invalid or expired SSO token.' });
    }
}


// --- CORE AUTHENTICATION LOGIC ---
class AngelAuthBridge {
    generateUserId() {
        return 'angel_' + Date.now() + '_' + crypto.randomBytes(4).toString('hex');
    }
    async hashPassword(password) {
        if (!password || password.length < 8) {
             throw new Error("Password must be at least 8 characters.");
        }
        return await bcrypt.hash(password, 12);
    }
    async verifyPassword(password, hash) {
        return await bcrypt.compare(password, hash);
    }
    generateToken(userId, scope = 'standard') {
        const payload = { 
            userId, 
            scope,
            legacyAccess: true, 
            timestamp: Date.now() 
        };
        return jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' });
    }
    verifyToken(token) {
        try {
            return jwt.verify(token, JWT_SECRET);
        } catch (error) {
            return null;
        }
    }
    async register(data) {
        const userId = this.generateUserId();
        const passwordHash = await this.hashPassword(data.password);
        
        const user = {
            userId,
            email: data.email,
            passwordHash,
            name: data.name,
            legacyName: data.legacyName,
            created: Date.now(),
            blockchainVerified: false
        };
        
        users.set(userId, user);
        return { userId, user };
    }
}

const authBridge = new AngelAuthBridge();


// --- PULSAR SECURITY ENDPOINT: BLOCKCHAIN VERIFICATION ---

app.post('/api/pulsar/verify-blockchain', async (req, res) => {
    const { address, signature, message, userId } = req.body;
    
    if (!address || !signature || !message || !userId) {
        return res.status(400).json({ error: 'Missing required fields for Pulsar verification.' });
    }

    try {
        const pulsarResponse = await pulsarCore.verifyWalletSignature(
            message, 
            signature, 
            address
        );

        const user = users.get(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found.' });
        }

        user.walletAddress = pulsarResponse.address;
        user.blockchainVerified = true;
        users.set(userId, user);

        const token = authBridge.generateToken(userId, 'pulsar-verified-sso');

        res.json({
            success: true,
            walletLinked: true,
            token,
            message: 'Pulsar Security activated. Wallet connected and SSO upgraded.'
        });

    } catch (error) {
        console.error('Pulsar Verification Error:', error.message);
        res.status(500).json({ error: `Pulsar verification failed: ${error.message}` });
    }
});


// --- NEW FEATURE ENDPOINT: MEGA DASHBOARD CALCULATOR ---

app.get('/api/dashboard/calculate-safe-window', verifySSO, async (req, res) => {
    // NOTE: In a production app, the dispatch data would be passed in the request body.
    // For this MVP, we run the simulated calculation engine.
    
    try {
        // Run the calculation engine (which calls the Gemini AI)
        const resultText = await calculateOptimalWindow();

        res.json({
            success: true,
            userId: req.userId,
            recommendation: resultText,
            message: 'Life Work Balance Mega Dashboard calculation complete.'
        });

    } catch (error) {
        console.error('Mega Dashboard Calculation Error:', error.message);
        res.status(500).json({ error: 'Mega Dashboard failed to run AI calculation.' });
    }
});


// --- VAULT ENCRYPTION SYSTEM ---
// ... (VaultEncryption class and logic unchanged, omitted for brevity)
class VaultEncryption {
    generateUserKey(userId, masterPassword) {
        return crypto.pbkdf2Sync(
            userId + masterPassword,
            ENCRYPTION_KEY, 
            600000, 
            32,
            'sha512'
        );
    }
    // ... (encryptVault, decryptVault methods omitted for brevity)
}
const vaultEncryption = new VaultEncryption();

// --- SSO & REGISTER ENDPOINTS ---
// ... (register, sso-login, validate-sso endpoints omitted for brevity, they are unchanged)


// --- SERVER STARTUP AND EXPORT ---

const PORT = process.env.PORT || 3005;

app.get('/', (req, res) => {
    const htmlPath = path.join(__dirname, 'public', 'index.html');
    if (fs.existsSync(htmlPath)) {
        res.sendFile(htmlPath);
    } else {
        res.send(`
<!DOCTYPE html>
<html>
<head>
    <title>Angel Cloud Welcome Center</title>
</head>
<body>
    <h1>Angel Cloud Welcome Center</h1>
    <p>Authentication Bridge is running on port ${PORT}.</p>
</body>
</html>
        `);
    }
});

app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║          ANGEL CLOUD AUTHENTICATION BRIDGE ACTIVE            ║
║  (Final MVP Integration)                                      ║
╠═══════════════════════════════════════════════════════════════╣
║  🔐 Security Status: OPERATIONAL                             ║
║  🌐 Port: ${PORT}                                           ║
║  🔗 URL: http://localhost:${PORT}                           ║
║                                                               ║
║  FEATURES: SSO, Legacy Vault, Pulsar Security, Mega Dashboard ║
╚═══════════════════════════════════════════════════════════════╝
    `);
});

// --- EXPORT FOR CLIENT TESTING ---
module.exports = { authBridge, vaults, vaultEncryption, users, verifySSO };