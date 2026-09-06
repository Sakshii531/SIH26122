import { MOCK_EXTRACTIONS_AND_MATCHES } from './mock/mockExtractions.js';

export const aiService = {
  /**
   * Run AI Entity Extraction on site input text
   */
  async extractEntities(rawText) {
    await new Promise(resolve => setTimeout(resolve, 600));
    return MOCK_EXTRACTIONS_AND_MATCHES[0].extractedEvent;
  },

  /**
   * Run Vector Semantic Matching against Primavera L5/L6 Activities
   */
  async matchActivity(extractedEvent) {
    await new Promise(resolve => setTimeout(resolve, 700));
    return MOCK_EXTRACTIONS_AND_MATCHES[0];
  },

  /**
   * Fetch all current AI extracted items with confidence scores
   */
  async getAllExtractedMatches() {
    return MOCK_EXTRACTIONS_AND_MATCHES;
  }
};
