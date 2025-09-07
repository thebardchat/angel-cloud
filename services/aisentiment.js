// Basic AI sentiment service (without OpenAI for now)
class AIAnalysisService {
  async analyze(text, options = {}) {
    try {
      // Simple keyword-based sentiment analysis for testing
      let sentimentScore = 0;
      
      const positiveWords = ['happy', 'good', 'great', 'love', 'excellent', 'wonderful'];
      const negativeWords = ['sad', 'bad', 'hate', 'terrible', 'awful', 'depressed', 'crisis'];
      
      const textLower = text.toLowerCase();
      
      positiveWords.forEach(word => {
        if (textLower.includes(word)) sentimentScore += 0.2;
      });
      
      negativeWords.forEach(word => {
        if (textLower.includes(word)) sentimentScore -= 0.3;
      });
      
      return {
        sentimentScore: Math.max(-1, Math.min(1, sentimentScore)),
        urgencyLevel: sentimentScore < -0.5 ? 'high' : 'medium',
        shaneBrainResponse: "I understand you're reaching out. Angels are here to help.",
        confidence: 0.7
      };
    } catch (error) {
      console.error('AI Analysis failed:', error);
      return {
        sentimentScore: 0,
        urgencyLevel: 'medium',
        shaneBrainResponse: "I'm here to help you.",
        confidence: 0.5
      };
    }
  }
}

module.exports = new AIAnalysisService();