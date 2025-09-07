const express = require('express');
const auth = require('../middleware/auth');
const Message = require('../models/Message');
const Angel = require('../models/Angel');
const router = express.Router();

// Send Help Request
router.post('/help-request', auth, async (req, res) => {
  try {
    const { content, urgency = 'medium', location } = req.body;

    const message = new Message({
      senderId: req.userId,
      content,
      messageType: 'help_request',
      urgency,
      location,
      timestamp: new Date()
    });

    await message.save();

    res.json({
      message: 'Help request sent to Angel Cloud',
      requestId: message._id,
      status: 'pending'
    });
  } catch (error) {
    console.error('Help request error:', error);
    res.status(500).json({ error: 'Failed to send help request' });
  }
});

// Get Messages
router.get('/messages', auth, async (req, res) => {
  try {
    const messages = await Message.find({
      $or: [
        { senderId: req.userId },
        { recipientId: req.userId }
      ]
    }).sort({ timestamp: -1 }).limit(50);

    res.json({ messages });
  } catch (error) {
    console.error('Get messages error:', error);
    res.status(500).json({ error: 'Failed to get messages' });
  }
});

module.exports = router;