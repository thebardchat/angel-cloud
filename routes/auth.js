const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Angel = require('../models/Angel');
const router = express.Router();

// Angel Registration
router.post('/register', async (req, res) => {
  try {
    const { email, password, displayName, location } = req.body;
    
    // Check if angel exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: 'Angel already exists' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create new angel account
    const user = new User({
      email,
      password: hashedPassword,
      displayName,
      location,
      role: 'user'
    });

    await user.save();

    // Create Angel profile - starts as New Born
    const angelProfile = new Angel({
      userId: user._id,
      angelLevel: 'New Born',
      halos: 0,
      helpCount: 0,
      location
    });

    await angelProfile.save();

    // Generate token
    const token = jwt.sign(
      { userId: user._id, angelId: angelProfile._id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.status(201).json({
      message: 'Welcome to Angel Cloud! You start as a New Born Angel',
      token,
      angel: {
        id: angelProfile._id,
        level: 'New Born',
        halos: 0,
        displayName
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Angel registration failed' });
  }
});

// Angel Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ error: 'Angel not found' });
    }

    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }

    const angelProfile = await Angel.findOne({ userId: user._id });

    const token = jwt.sign(
      { userId: user._id, angelId: angelProfile._id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      message: `Welcome back, ${angelProfile.angelLevel} Angel!`,
      token,
      angel: {
        id: angelProfile._id,
        level: angelProfile.angelLevel,
        halos: angelProfile.halos,
        displayName: user.displayName
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Angel login failed' });
  }
});

module.exports = router;