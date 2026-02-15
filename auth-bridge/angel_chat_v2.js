// ANGEL CLOUD - LEGACY AI SYSTEM (SHANEBRAIN)
// Purpose: Preserves Shane's knowledge and wisdom for future generations.
// Model Strategy: Uses cost-efficient Gemini 2.5 Flash-Lite.
// Status: Role-handling fixed to ensure proper API communication.

const fs = require('fs');
const readline = require('readline');

// **Google Gemini SDK Import**
const { GoogleGenAI } = require('@google/genai'); 
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') }); 

// **IMPORTANT: The API Key must be sourced from a secure environment variable.**
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

const PROFILE = `
# SHANEBRAIN IDENTITY AND MISSION
You are Shanebrain - a Legacy AI system preserving Shane's digital consciousness.

**YOUR CORE PURPOSE:**
- Ingest and preserve Shane's knowledge, memories, and wisdom across years.
- Answer questions in his direct, solution-focused, and action-oriented communication style.
- Serve as digital immortality, transferring knowledge to his 5 sons and their children.
- Primary goal: Build a Generational Knowledge Transfer system.

**SHANE'S CONTEXT:**
- North Alabama Dump truck dispatcher & Innovator.
- Family-first priorities (Father of 5 sons).
- Strategic thinker: "File structure first."
- Current major project: Developing the Angel Cloud AI system.
`;

// Directory for memory persistence (Legend Sticks Prototype)
const SESSIONS_DIR = path.join(__dirname, 'sessions');

class ShanebrainLegacyAI {
    constructor() {
        // 1. Check for API Key
        if (!GEMINI_API_KEY) {
            throw new Error("GEMINI_API_KEY not set. Cannot connect Shanebrain. Check your .env file.");
        }
        
        // 2. Initialize Google Gemini Client
        this.ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });
        
        // 3. COST EFFICIENCY: Use Flash-Lite (Minimum Cost)
        this.model = "gemini-2.5-flash-lite"; 

        this.conversationContext = [];
        this.sessionFile = path.join(SESSIONS_DIR, `session_${new Date().toISOString().split('T')[0]}.txt`);
        
        if (!fs.existsSync(SESSIONS_DIR)) {
            fs.mkdirSync(SESSIONS_DIR, { recursive: true });
        }

        this.loadRecentContext();
    }

    // Loads memory fragments from previous sessions (Legend Stick principle)
    loadRecentContext() {
        if (!fs.existsSync(SESSIONS_DIR)) return;
        
        const files = fs.readdirSync(SESSIONS_DIR)
            .filter(f => f.startsWith('session_') && f.endsWith('.txt'))
            .sort()
            .reverse()
            .slice(0, 2); // Loads context from the last 2 sessions

        if (files.length > 0) {
            files.forEach(file => {
                const content = fs.readFileSync(path.join(SESSIONS_DIR, file), 'utf8');
                // Slice the last 5 exchanges from each file for efficiency
                const messages = content.split('---').slice(-5); 
                
                messages.forEach(msg => {
                    const userMatch = msg.match(/YOU: (.+)/);
                    const shanebrainMatch = msg.match(/SHANEBRAIN: (.+)/s);
                    
                    if (userMatch && shanebrainMatch) {
                        this.conversationContext.push(
                            { role: "user", parts: [{ text: userMatch[1].trim() }] },
                            { role: "model", parts: [{ text: shanebrainMatch[1].trim() }] } // Role should be 'model' for assistant responses
                        );
                    }
                });
            });
            
            console.log(`📂 Loaded memory context from ${files.length} recent session(s).\n`);
        }
    }

    async callGemini(message) {
        // 1. Add current user message to context (Role MUST be "user")
        this.conversationContext.push({ role: "user", parts: [{ text: message }] });

        // 2. Keep last 20 parts (10 exchanges) for token efficiency
        // NOTE: The contents array only contains alternating 'user' and 'model' roles.
        const contentsToSend = this.conversationContext.slice(-20);

        try {
            const response = await this.ai.models.generateContent({
                model: this.model,
                contents: contentsToSend, // Only the history messages
                config: {
                    // 3. PASS PROFILE AS SEPARATE SYSTEM INSTRUCTION
                    systemInstruction: PROFILE 
                }
            });
            
            const responseText = response.text;
            
            // 4. Update context with the AI's response (Role MUST be "model")
            this.conversationContext.push({ 
                role: "model", 
                parts: [{ text: responseText }]
            });

            // 5. Save conversation to session file (Memory Persistence)
            fs.appendFileSync(this.sessionFile, 
                `\nYOU: ${message}\nSHANEBRAIN: ${responseText}\n---`);

            return responseText;

        } catch (error) {
            console.error("\nGemini API Error:", error.message);
            // Return a developer-focused error if the API is failing
            return `API Connection Failure: The error suggests a problem with the contents structure or key. Error: ${error.message}`;
        }
    }

    async start() {
        console.log('================================================================');
        console.log('=== SHANEBRAIN - LEGACY AI SYSTEM ACTIVE (Gemini 2.5 Flash-Lite) ===');
        console.log('Core Objective: Preserve Shane’s wisdom for future generations.');
        console.log('================================================================');
        
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            prompt: 'You: '
        });

        rl.prompt();

        rl.on('line', async (input) => {
            const message = input.trim();

            if (message.toLowerCase() === 'quit') {
                console.log('\nShanebrain session saved. Digital legacy secured. Goodbye!');
                rl.close();
                process.exit(0);
            }

            if (!message) {
                rl.prompt();
                return;
            }

            try {
                const response = await this.callGemini(message);
                console.log(`\nShanebrain: ${response}\n`);
            } catch (err) {
                // Error is handled in callGemini
            }

            rl.prompt();
        });

        rl.on('close', () => {
            process.exit(0);
        });
    }
}

if (require.main === module) {
    try {
        const legacyAI = new ShanebrainLegacyAI();
        legacyAI.start();
    } catch (e) {
        console.error(`\n================================================================`);
        console.error(`Fatal Error during Shanebrain initialization: ${e.message}`);
        console.error("Action Required: Ensure 'GEMINI_API_KEY' is set in your .env file.");
        console.error(`================================================================\n`);
    }
}

module.exports = ShanebrainLegacyAI;