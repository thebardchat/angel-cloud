/**
 * Weaviate API Routes for Angel Cloud
 *
 * Endpoints for interacting with Weaviate vector database:
 * - /api/weaviate/status - Health check
 * - /api/weaviate/search - Search legacy knowledge
 * - /api/weaviate/conversations - Get/create conversations
 * - /api/weaviate/analyze - AI analysis with context
 */

const express = require('express');
const auth = require('../middleware/auth');
const weaviate = require('../utils/weaviate');
const logger = require('../utils/logger');

const router = express.Router();

/**
 * GET /api/weaviate/status
 * Check Weaviate connection status
 */
router.get('/status', async (req, res) => {
  try {
    const ready = await weaviate.isReady();
    const stats = ready ? await weaviate.getStats() : null;

    res.json({
      status: ready ? 'connected' : 'disconnected',
      stats
    });
  } catch (error) {
    logger.error('Weaviate status check failed:', error);
    res.status(500).json({ error: 'Failed to check Weaviate status' });
  }
});

/**
 * GET /api/weaviate/search
 * Search legacy knowledge
 * Query params: q (search text), category, limit
 */
router.get('/search', async (req, res) => {
  try {
    const { q, category, limit = 10 } = req.query;

    const results = await weaviate.searchLegacy(q, category, parseInt(limit));

    res.json({
      count: results.length,
      results
    });
  } catch (error) {
    logger.error('Legacy search failed:', error);
    res.status(500).json({ error: 'Search failed' });
  }
});

/**
 * GET /api/weaviate/conversations
 * Get recent conversations (requires auth)
 * Query params: limit, session_id, mode
 */
router.get('/conversations', auth, async (req, res) => {
  try {
    const { limit = 20, session_id, mode } = req.query;

    const conversations = await weaviate.getRecentConversations(
      parseInt(limit),
      session_id,
      mode
    );

    res.json({
      count: conversations.length,
      conversations
    });
  } catch (error) {
    logger.error('Failed to get conversations:', error);
    res.status(500).json({ error: 'Failed to retrieve conversations' });
  }
});

/**
 * POST /api/weaviate/conversations
 * Log a conversation message (requires auth)
 * Body: { message, role, mode, session_id }
 */
router.post('/conversations', auth, async (req, res) => {
  try {
    const { message, role = 'user', mode = 'logibot', session_id } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    const result = await weaviate.logConversation(message, role, mode, session_id);

    res.json({
      success: true,
      id: result.id
    });
  } catch (error) {
    logger.error('Failed to log conversation:', error);
    res.status(500).json({ error: 'Failed to log conversation' });
  }
});

/**
 * POST /api/weaviate/analyze
 * Analyze text with context from legacy knowledge (requires auth)
 * Body: { text, mode }
 */
router.post('/analyze', auth, async (req, res) => {
  try {
    const { text, mode = 'logibot' } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    const analysis = await weaviate.analyzeWithContext(text, mode);

    // Log the user message
    await weaviate.logConversation(text, 'user', mode, req.body.session_id);

    res.json({ analysis });
  } catch (error) {
    logger.error('Analysis failed:', error);
    res.status(500).json({ error: 'Analysis failed' });
  }
});

/**
 * POST /api/weaviate/knowledge
 * Add new knowledge entry (requires auth)
 * Body: { content, category, source }
 */
router.post('/knowledge', auth, async (req, res) => {
  try {
    const { content, category = 'general', source = 'manual' } = req.body;

    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const result = await weaviate.addLegacyKnowledge(content, category, source);

    res.json({
      success: true,
      id: result.id
    });
  } catch (error) {
    logger.error('Failed to add knowledge:', error);
    res.status(500).json({ error: 'Failed to add knowledge' });
  }
});

/**
 * POST /api/weaviate/crisis
 * Log a crisis event (admin only in production)
 * Body: { input_text, severity }
 */
router.post('/crisis', auth, async (req, res) => {
  try {
    const { input_text, severity = 'medium' } = req.body;

    if (!input_text) {
      return res.status(400).json({ error: 'input_text is required' });
    }

    const result = await weaviate.logCrisis(input_text, severity);

    logger.warn('Crisis event logged via API', {
      userId: req.userId,
      severity
    });

    res.json({
      success: true,
      id: result.id
    });
  } catch (error) {
    logger.error('Failed to log crisis:', error);
    res.status(500).json({ error: 'Failed to log crisis event' });
  }
});

module.exports = router;
