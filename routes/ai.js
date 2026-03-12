const express = require('express');
const auth = require('../middleware/auth');
const weaviate = require('../utils/weaviate');
const logger = require('../utils/logger');
const router = express.Router();

/**
 * POST /api/ai/analyze
 * Analyze text with context from ShaneBrain knowledge base
 */
router.post('/analyze', auth, async (req, res) => {
  try {
    const { text, mode = 'logibot', session_id } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    // Get analysis with Weaviate context
    const analysis = await weaviate.analyzeWithContext(text, mode);

    // Log the conversation
    await weaviate.logConversation(text, 'user', mode, session_id).catch(() => {});

    res.json({ analysis });
  } catch (error) {
    logger.error('AI analysis failed:', error);
    res.status(500).json({ error: 'Analysis failed' });
  }
});

/**
 * POST /api/ai/chat
 * Get AI response with full context injection
 * This endpoint provides context for external LLM calls
 */
router.post('/chat', auth, async (req, res) => {
  try {
    const { message, mode = 'shanebrain', session_id, include_context = true } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Log user message
    await weaviate.logConversation(message, 'user', mode, session_id).catch(() => {});

    // Get relevant context from brain search
    let context = '';
    if (include_context) {
      try {
        context = await weaviate.getContextForPrompt(message, 1500);
      } catch (e) {
        logger.warn('Failed to get context:', e);
      }
    }

    // Check for crisis indicators
    const crisisKeywords = ['suicide', 'kill myself', 'end it all', 'want to die', 'self harm'];
    const hasCrisis = crisisKeywords.some(kw => message.toLowerCase().includes(kw));

    if (hasCrisis) {
      await weaviate.logCrisis(message, 'high').catch(() => {});
    }

    // Build the response with context
    // In production, this would call Ollama or another LLM
    const response = {
      context,
      hasCrisis,
      mode,
      session_id: session_id || `session_${Date.now()}`,
      systemPrompt: buildSystemPrompt(mode, context),
      // Placeholder response - replace with actual LLM call
      message: hasCrisis
        ? "I hear you, and I want you to know that you matter. If you're in crisis, please reach out to the 988 Suicide & Crisis Lifeline. I'm here to listen."
        : "I'm processing your message with the context of our previous conversations."
    };

    res.json(response);
  } catch (error) {
    logger.error('Chat endpoint failed:', error);
    res.status(500).json({ error: 'Chat failed' });
  }
});

/**
 * GET /api/ai/context
 * Get relevant context for a query (useful for debugging)
 */
router.get('/context', auth, async (req, res) => {
  try {
    const { q, limit = 3 } = req.query;

    if (!q) {
      return res.status(400).json({ error: 'Query parameter q is required' });
    }

    const results = await weaviate.brainSearch(q, {
      includeLegacy: true,
      includeMemory: true,
      includeConversation: true,
      limit: parseInt(limit)
    });

    const formattedContext = await weaviate.getContextForPrompt(q);

    res.json({
      query: q,
      results,
      formattedContext
    });
  } catch (error) {
    logger.error('Context retrieval failed:', error);
    res.status(500).json({ error: 'Failed to get context' });
  }
});

/**
 * Build system prompt based on mode and context
 */
function buildSystemPrompt(mode, context) {
  const basePrompts = {
    logibot: `You are LogiBot, an operational AI assistant for SRM Trucking dispatch operations. Be direct, efficient, and focused on logistics.`,
    shanebrain: `You are ShaneBrain, Shane's personal AI assistant with access to his knowledge base, family values, and work context. Be helpful, remember context, and align with Shane's communication style - direct, no fluff, action-oriented.`,
    angel: `You are an Angel Cloud wellness companion. Be compassionate, supportive, and focused on mental wellness. Always prioritize user safety.`
  };

  let prompt = basePrompts[mode] || basePrompts.shanebrain;

  if (context) {
    prompt += `\n\n## Relevant Context\n${context}`;
  }

  prompt += `\n\n## Guidelines
- Be direct and concise
- Don't repeat what the user said
- Don't apologize unnecessarily
- Take action rather than explaining
- If crisis indicators are detected, prioritize safety`;

  return prompt;
}

module.exports = router;
