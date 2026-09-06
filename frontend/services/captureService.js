import { MOCK_EXTRACTIONS_AND_MATCHES, MOCK_VOICE_TRANSCRIPT } from './mock/mockExtractions.js';

export const captureService = {
  /**
   * Upload Daily Site Report (PDF / Text)
   */
  async uploadDSR(file) {
    // Simulate network parsing delay
    await new Promise(resolve => setTimeout(resolve, 800));
    return {
      success: true,
      fileId: 'FILE-' + Date.now(),
      fileName: file.name || 'DSR_SiteReport_20260905.pdf',
      parsedEvent: MOCK_EXTRACTIONS_AND_MATCHES[0].extractedEvent
    };
  },

  /**
   * Upload Excel Spreadsheet
   */
  async uploadExcel(file) {
    await new Promise(resolve => setTimeout(resolve, 800));
    return {
      success: true,
      fileId: 'EXCEL-' + Date.now(),
      fileName: file.name || 'Weekly_Log_W36.xlsx',
      rowCount: 42,
      parsedEvent: MOCK_EXTRACTIONS_AND_MATCHES[2].extractedEvent
    };
  },

  /**
   * Upload Voice Record Audio File
   */
  async uploadVoice(file) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      success: true,
      fileId: 'VOICE-' + Date.now(),
      fileName: file.name || 'AUDIO_REC_ErRajesh_20260905.wav',
      durationSeconds: 65,
      transcript: MOCK_VOICE_TRANSCRIPT,
      parsedEvent: MOCK_EXTRACTIONS_AND_MATCHES[1].extractedEvent
    };
  }
};
