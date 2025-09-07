const express = require('express');
const auth = require('../middleware/auth');
const router = express.Router();

// Basic AI endpoint (without OpenAI for now)
router.post('/analyze', auth, async (req, res) => {
  try {
    const { text } = req.body;
    
    // Simple sentiment analysis placeholder
    const analysis = {
      sentimentScore: text.includes('sad') || text.includes('depressed') ? -0.6 : 0.2,
      urgencyLevel: text.includes('crisis') || text.includes('emergency') ? 'high' : 'medium',
      shaneBrainResponse: "I'm here to help you through this."
    };

    res.json({ analysis });
  } catch (error) {
    res.status(500).json({ error: 'Analysis failed' });
  }
});

module.exports = router;