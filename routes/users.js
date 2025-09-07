const express = require('express');
const auth = require('../middleware/auth');
const User = require('../models/User');
const Angel = require('../models/Angel');
const router = express.Router();

// Get Angel Profile
router.get('/profile', auth, async (req, res) => {
  try {
    const user = await User.findById(req.userId).select('-password');
    const angel = await Angel.findOne({ userId: req.userId });

    res.json({
      user,
      angel: {
        level: angel.angelLevel,
        halos: angel.halos,
        helpCount: angel.helpCount,
        location: angel.location,
        joinedDate: angel.joinedDate
      }
    });
  } catch (error) {
    console.error('Profile error:', error);
    res.status(500).json({ error: 'Failed to get profile' });
  }
});

module.exports = router;