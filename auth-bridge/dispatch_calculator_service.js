// DISPATCH CALCULATOR SERVICE (MEGA DASHBOARD ENGINE)
// Purpose: Calculates the optimal personal/family time window using AI.
// Model Strategy: Uses cost-efficient Gemini 2.5 Flash-Lite.

const { GoogleGenAI } = require('@google/genai'); 
const path = require('path');
const dotenv = require('dotenv'); // Explicitly import dotenv

// Load environment variables (API Key) from .env
dotenv.config({ path: path.join(__dirname, '.env') }); 

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

if (!GEMINI_API_KEY) {
    console.error("FATAL: GEMINI_API_KEY not set. Cannot run calculator service. Check your .env file.");
    process.exit(1);
}

const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });
const model = "gemini-2.5-flash-lite"; // Cost-efficient model

// --- SIMULATED REAL-TIME DISPATCH DATA (The three core inputs) ---
const DISPATCH_DATA = {
    // 1. Current Driver/Truck Availability Status
    activeDrivers: 15,
    scheduledLoadsNext4Hours: 12,
    availableTrucks: 18,
    
    // 2. Next Scheduled Material Pickup ETA & Destination
    nextCriticalLoadTime: "10:30 AM",
    nextCriticalPickup: "Mt Hope - Plant 592",
    nextCriticalDestination: "Decatur Project Site",
    
    // 3. Projected Revenue/Cost-per-Minute Value
    loadRevenuePerTon: 12.10, // Crusher Run price [cite: 2025-06-19]
    estimatedTonnage: 25,
    costPerMinuteDelay: 1.50 // Estimated cost of idle driver time and fuel
};

// --- SHANEBRAIN INSTRUCTION ---
const SYSTEM_INSTRUCTION = `
You are Shanebrain, acting as the Life Work Balance Mega Dashboard. Your task is to calculate and provide a SINGLE, ACTIONABLE, OPTIMAL TIME WINDOW for personal/family time.

Your response MUST be direct, solution-focused, and based ONLY on the provided JSON data. You must include the financial risk justification.

**Instructions:**
1. Calculate the 'Buffer Capacity' (Drivers - Loads).
2. Calculate the 'Financial Risk of Delay' (Cost-per-Minute).
3. Determine the optimal 'Safe Window' between now and the Next Critical Load Time (${DISPATCH_DATA.nextCriticalLoadTime}).
4. Your FINAL OUTPUT must be only the recommendation and the justification.
`;


async function calculateOptimalWindow() {
    const NOW = new Date();
    // Use a simplified logic for calculating time until critical for this simulation
    const timeUntilCritical = (new Date(new Date().toDateString() + ' ' + DISPATCH_DATA.nextCriticalLoadTime) - NOW) / 60000; // Time difference in minutes

    if (timeUntilCritical < 30) {
        return "CRITICAL FAILURE: No safe window available. Next load is too soon. Operational stress is too high.";
    }

    const prompt = `
    CURRENT TIME: ${NOW.toLocaleTimeString()}
    TIME UNTIL CRITICAL LOAD (10:30 AM) in minutes: ${Math.round(timeUntilCritical)}

    DISPATCH DATA FOR ANALYSIS:
    - AVAILABLE TRUCKS/DRIVERS: ${DISPATCH_DATA.activeDrivers} / ${DISPATCH_DATA.availableTrucks}
    - LOADS IN NEXT 4 HOURS: ${DISPATCH_DATA.scheduledLoadsNext4Hours}
    - NEXT PICKUP: ${DISPATCH_DATA.nextCriticalPickup}
    - NEXT DESTINATION: ${DISPATCH_DATA.nextCriticalDestination}
    - LOAD REVENUE: $${DISPATCH_DATA.loadRevenuePerTon} per ton (x ${DISPATCH_DATA.estimatedTonnage} tons)
    - COST PER MINUTE DELAY: $${DISPATCH_DATA.costPerMinuteDelay}
    
    CALCULATE the optimal safe time window for Shane and provide the financial justification.
    `;

    try {
        console.log("=======================================================");
        console.log("🧠 Consulting Shanebrain Legacy AI...");
        
        const response = await ai.models.generateContent({
            model: model,
            contents: [
                { role: "user", parts: [{ text: prompt }] }
            ],
            config: {
                systemInstruction: SYSTEM_INSTRUCTION
            }
        });

        console.log("=======================================================");
        console.log("✅ MEGA DASHBOARD RESULT:");
        console.log("=======================================================");
        console.log(response.text.trim());
        console.log("=======================================================");
        
        // Return the text for the main server to integrate
        return response.text.trim();

    } catch (error) {
        console.error("FATAL GEMINI API ERROR:", error.message);
        console.log("Check your GEMINI_API_KEY and network connection.");
        throw new Error("AI Calculation Failed");
    }
}

// Ensure the necessary Node.js modules are installed before running
if (require.main === module) {
    calculateOptimalWindow();
}

module.exports = calculateOptimalWindow;