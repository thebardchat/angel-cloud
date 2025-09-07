// Basic angel matching service
const Angel = require('../models/Angel');

class AngelMatchingService {
  async findAvailableAngels(location, urgency, emotionalNeeds, limit = 10) {
    try {
      const query = {
        isActive: true,
        isAvailable: true
      };

      if (location) {
        query.location = new RegExp(location, 'i');
      }

      const availableAngels = await Angel.find(query)
        .populate('userId', 'displayName')
        .sort({ halos: -1 })
        .limit(limit);

      return availableAngels.map(angel => ({
        angelId: angel._id,
        userId: angel.userId._id,
        displayName: angel.userId.displayName,
        angelLevel: angel.angelLevel,
        halos: angel.halos,
        location: angel.location
      }));
    } catch (error) {
      console.error('Angel matching failed:', error);
      return [];
    }
  }
}

module.exports = new AngelMatchingService();