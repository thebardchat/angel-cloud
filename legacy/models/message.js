const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
  senderId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  recipientId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  content: {
    type: String,
    required: true,
    maxlength: 2000
  },
  messageType: {
    type: String,
    enum: ['help_request', 'angel_response', 'follow_up', 'crisis_alert'],
    required: true
  },
  urgency: {
    type: String,
    enum: ['low', 'medium', 'high', 'crisis'],
    default: 'medium'
  },
  location: String,
  sentimentScore: {
    type: Number,
    min: -1,
    max: 1
  },
  status: {
    type: String,
    enum: ['pending', 'responded', 'resolved'],
    default: 'pending'
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Message', messageSchema);