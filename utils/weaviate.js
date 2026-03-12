/**
 * Weaviate Integration for Angel Cloud / ShaneBrain
 *
 * Node.js utilities for interacting with the Weaviate vector database.
 * Handles conversation logging, legacy knowledge search, and crisis detection logging.
 */

const logger = require('./logger');

// Weaviate configuration
const WEAVIATE_URL = process.env.WEAVIATE_URL || 'http://localhost:8080';

/**
 * Make a GraphQL query to Weaviate
 */
async function weaviateQuery(query) {
  try {
    const response = await fetch(`${WEAVIATE_URL}/v1/graphql`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      throw new Error(`Weaviate query failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    logger.error('Weaviate query error:', error);
    throw error;
  }
}

/**
 * Create an object in Weaviate
 */
async function createObject(className, properties) {
  try {
    const response = await fetch(`${WEAVIATE_URL}/v1/objects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        class: className,
        properties
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create object: ${error}`);
    }

    return await response.json();
  } catch (error) {
    logger.error('Weaviate create error:', error);
    throw error;
  }
}

/**
 * Check if Weaviate is ready
 */
async function isReady() {
  try {
    const response = await fetch(`${WEAVIATE_URL}/v1/.well-known/ready`);
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Log a conversation message
 *
 * @param {string} message - The message text
 * @param {string} role - 'user' or 'assistant'
 * @param {string} mode - Chat mode (logibot, shanebrain, angel)
 * @param {string} sessionId - Session identifier
 */
async function logConversation(message, role, mode = 'logibot', sessionId = null) {
  const properties = {
    message,
    role,
    mode,
    timestamp: new Date().toISOString(),
    session_id: sessionId || `session_${Date.now()}`
  };

  return createObject('Conversation', properties);
}

/**
 * Log a crisis detection event
 *
 * @param {string} inputText - Text that triggered the detection
 * @param {string} severity - low, medium, high, critical
 */
async function logCrisis(inputText, severity = 'medium') {
  const validSeverities = ['low', 'medium', 'high', 'critical'];
  if (!validSeverities.includes(severity)) {
    severity = 'medium';
  }

  const properties = {
    input_text: inputText,
    severity,
    timestamp: new Date().toISOString()
  };

  logger.warn(`Crisis event logged: severity=${severity}`, { inputText: inputText.substring(0, 100) });

  return createObject('CrisisLog', properties);
}

/**
 * Search LegacyKnowledge for relevant wisdom
 *
 * @param {string} searchText - Text to search for
 * @param {string} category - Filter by category (family, faith, technical, philosophy, general)
 * @param {number} limit - Max results
 */
async function searchLegacy(searchText, category = null, limit = 5) {
  let whereClause = '';
  if (category) {
    whereClause = `where: { path: ["category"], operator: Equal, valueString: "${category}" }`;
  }

  // Use BM25 search if we have search text
  let searchClause = '';
  if (searchText) {
    searchClause = `bm25: { query: "${searchText.replace(/"/g, '\\"')}", properties: ["content"] }`;
  }

  const query = `{
    Get {
      LegacyKnowledge(
        limit: ${limit}
        ${searchClause ? searchClause : ''}
        ${whereClause}
      ) {
        content
        category
        source
      }
    }
  }`;

  const result = await weaviateQuery(query);
  return result.data?.Get?.LegacyKnowledge || [];
}

/**
 * Get recent conversation history
 *
 * @param {number} limit - Max results
 * @param {string} sessionId - Filter by session
 * @param {string} mode - Filter by mode
 */
async function getRecentConversations(limit = 20, sessionId = null, mode = null) {
  let whereClause = '';
  const filters = [];

  if (sessionId) {
    filters.push(`{ path: ["session_id"], operator: Equal, valueString: "${sessionId}" }`);
  }
  if (mode) {
    filters.push(`{ path: ["mode"], operator: Equal, valueString: "${mode}" }`);
  }

  if (filters.length === 1) {
    whereClause = `where: ${filters[0]}`;
  } else if (filters.length > 1) {
    whereClause = `where: { operator: And, operands: [${filters.join(', ')}] }`;
  }

  const query = `{
    Get {
      Conversation(
        limit: ${limit}
        sort: [{ path: ["timestamp"], order: desc }]
        ${whereClause}
      ) {
        message
        role
        mode
        timestamp
        session_id
      }
    }
  }`;

  const result = await weaviateQuery(query);
  return result.data?.Get?.Conversation || [];
}

/**
 * Add new knowledge to LegacyKnowledge
 *
 * @param {string} content - The knowledge content
 * @param {string} category - Category (family, faith, technical, philosophy, general)
 * @param {string} source - Source identifier
 */
async function addLegacyKnowledge(content, category = 'general', source = 'manual') {
  const properties = {
    content,
    category,
    source
  };

  return createObject('LegacyKnowledge', properties);
}

/**
 * Get class statistics
 */
async function getStats() {
  const classes = ['Conversation', 'LegacyKnowledge', 'CrisisLog', 'SessionMemory'];
  const stats = {};

  for (const className of classes) {
    try {
      const query = `{ Aggregate { ${className} { meta { count } } } }`;
      const result = await weaviateQuery(query);
      stats[className] = result.data?.Aggregate?.[className]?.[0]?.meta?.count || 0;
    } catch {
      stats[className] = 0;
    }
  }

  return stats;
}

/**
 * Search SessionMemory for relevant past sessions
 *
 * @param {string} searchText - Text to search for
 * @param {number} limit - Max results
 */
async function searchMemory(searchText, limit = 5) {
  const searchClause = searchText
    ? `bm25: { query: "${searchText.replace(/"/g, '\\"')}", properties: ["content"] }`
    : '';

  const query = `{
    Get {
      SessionMemory(
        limit: ${limit}
        ${searchClause}
      ) {
        content
        section
        session_file
        session_date
      }
    }
  }`;

  const result = await weaviateQuery(query);
  return result.data?.Get?.SessionMemory || [];
}

/**
 * Unified brain search across all knowledge sources
 *
 * @param {string} searchText - Text to search for
 * @param {Object} options - Search options
 * @param {boolean} options.includeLegacy - Include LegacyKnowledge (default: true)
 * @param {boolean} options.includeMemory - Include SessionMemory (default: true)
 * @param {boolean} options.includeConversation - Include Conversation (default: false)
 * @param {number} options.limit - Results per source (default: 3)
 */
async function brainSearch(searchText, options = {}) {
  const {
    includeLegacy = true,
    includeMemory = true,
    includeConversation = false,
    limit = 3
  } = options;

  const results = {
    legacy: [],
    memory: [],
    conversation: []
  };

  const searches = [];

  if (includeLegacy) {
    searches.push(
      searchLegacy(searchText, null, limit)
        .then(r => { results.legacy = r; })
        .catch(() => {})
    );
  }

  if (includeMemory) {
    searches.push(
      searchMemory(searchText, limit)
        .then(r => { results.memory = r; })
        .catch(() => {})
    );
  }

  if (includeConversation) {
    const query = `{
      Get {
        Conversation(
          limit: ${limit}
          bm25: { query: "${searchText.replace(/"/g, '\\"')}", properties: ["message"] }
        ) {
          message
          role
          mode
          timestamp
        }
      }
    }`;
    searches.push(
      weaviateQuery(query)
        .then(r => { results.conversation = r.data?.Get?.Conversation || []; })
        .catch(() => {})
    );
  }

  await Promise.all(searches);
  return results;
}

/**
 * Get context for LLM prompt injection
 *
 * Returns a formatted string with relevant knowledge from all sources
 * that can be injected into an LLM prompt.
 *
 * @param {string} query - User query to find relevant context for
 * @param {number} maxTokens - Approximate max tokens (default: 1500)
 */
async function getContextForPrompt(query, maxTokens = 1500) {
  const searchResults = await brainSearch(query, {
    includeLegacy: true,
    includeMemory: true,
    includeConversation: false,
    limit: 3
  });

  const contextParts = [];
  let estimatedTokens = 0;

  // Add legacy knowledge first (highest priority)
  for (const item of searchResults.legacy) {
    const chunk = `[Knowledge - ${item.category || 'general'}]\n${item.content}\n`;
    const chunkTokens = Math.ceil(chunk.length / 4);
    if (estimatedTokens + chunkTokens > maxTokens) break;
    contextParts.push(chunk);
    estimatedTokens += chunkTokens;
  }

  // Add session memory
  for (const item of searchResults.memory) {
    const chunk = `[Session - ${item.section || 'memory'}]\n${item.content}\n`;
    const chunkTokens = Math.ceil(chunk.length / 4);
    if (estimatedTokens + chunkTokens > maxTokens) break;
    contextParts.push(chunk);
    estimatedTokens += chunkTokens;
  }

  return contextParts.join('\n---\n');
}

/**
 * Enhanced AI analysis that uses legacy knowledge
 *
 * @param {string} text - User input text
 * @param {string} mode - Chat mode
 */
async function analyzeWithContext(text, mode = 'logibot') {
  // Check for crisis keywords
  const crisisKeywords = ['suicide', 'kill myself', 'end it all', 'want to die', 'hopeless'];
  const hasCrisisIndicators = crisisKeywords.some(kw => text.toLowerCase().includes(kw));

  if (hasCrisisIndicators) {
    // Log the crisis event
    await logCrisis(text, 'high');
    logger.warn('Crisis indicators detected in user input');
  }

  // Search for relevant legacy knowledge
  const relevantKnowledge = await searchLegacy(text, null, 3);

  // Determine sentiment (simple heuristic)
  const negativeWords = ['sad', 'depressed', 'anxious', 'worried', 'scared', 'angry', 'hurt'];
  const positiveWords = ['happy', 'grateful', 'blessed', 'hopeful', 'excited', 'love'];

  const textLower = text.toLowerCase();
  const negCount = negativeWords.filter(w => textLower.includes(w)).length;
  const posCount = positiveWords.filter(w => textLower.includes(w)).length;

  let sentimentScore = 0;
  if (negCount > posCount) sentimentScore = -0.3 * negCount;
  else if (posCount > negCount) sentimentScore = 0.3 * posCount;
  sentimentScore = Math.max(-1, Math.min(1, sentimentScore));

  return {
    sentimentScore,
    hasCrisisIndicators,
    urgencyLevel: hasCrisisIndicators ? 'critical' : (sentimentScore < -0.5 ? 'high' : 'normal'),
    relevantKnowledge: relevantKnowledge.map(k => ({
      content: k.content,
      category: k.category
    })),
    mode
  };
}

module.exports = {
  isReady,
  logConversation,
  logCrisis,
  searchLegacy,
  searchMemory,
  brainSearch,
  getContextForPrompt,
  getRecentConversations,
  addLegacyKnowledge,
  getStats,
  analyzeWithContext,
  weaviateQuery,
  createObject
};
