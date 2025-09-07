const express = require('express');
const Angel = require('../models/Angel');
const router = express.Router();

// Get Angel Leaderboard
router.get('/leaderboard', async (req, res) => {
  try {
    const angels = await Angel.find({ isActive: true })
      .populate('userId', 'displayName')
      .sort({ halos: -1, helpCount: -1 })
      .limit(20);

    const leaderboard = angels.map((angel, index) => ({
      rank: index + 1,
      displayName: angel.userId.displayName,
      angelLevel: angel.angelLevel,
      halos: angel.halos,
      helpCount: angel.helpCount
    }));

    res.json({ leaderboard });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get leaderboard' });
  }
});

module.exports = router;