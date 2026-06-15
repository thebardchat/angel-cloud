const mongoose = require('mongoose');

const angelSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  angelLevel: {
    type: String,
    enum: ['New Born', 'Young Angel', 'Growing Angel', 'Helping Angel', 'Guardian Angel', 'Angel'],
    default: 'New Born'
  },
  halos: {
    type: Number,
    default: 0,
    min: 0
  },
  helpCount: {
    type: Number,
    default: 0,
    min: 0
  },
  location: {
    type: String,
    required: true
  },
  specialties: [{
    type: String,
    enum: ['anxiety', 'depression', 'relationships', 'work_stress', 'family_issues', 'general_support']
  }],
  isActive: {
    type: Boolean,
    default: true
  },
  isAvailable: {
    type: Boolean,
    default: true
  },
  joinedDate: {
    type: Date,
    default: Date.now
  },
  lastActive: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Angel', angelSchema);