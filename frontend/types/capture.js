/**
 * @typedef {'DSR_PDF' | 'EXCEL' | 'VOICE_MEMO'} IngestionSourceType
 * 
 * @typedef {Object} ExtractedEntity
 * @property {string} id - Extraction ID
 * @property {IngestionSourceType} sourceType - Type of source file
 * @property {string} sourceFileName - File name (e.g. 'DSR_2026_09_05_Pier14.pdf')
 * @property {string} sourceRefLocation - Specific location in file (e.g. 'Page 2, Section 3.1' or 'Sheet1!B14' or '01:24 timestamp')
 * @property {string} rawText - Exact raw text extracted from site report
 * @property {string} extractedActivity - Parsed activity description
 * @property {number} [quantity] - Parsed quantity (e.g. 120)
 * @property {string} [unit] - Unit of measurement (e.g. 'm³')
 * @property {string} [extractedStart] - Extracted start date (ISO string)
 * @property {string} [extractedFinish] - Extracted finish date (ISO string)
 * @property {string[]} [equipmentUsed] - List of equipment mentioned (e.g. ['Putzmeister Boom Pump', 'Batching Plant Line A'])
 * @property {number} [workforceCount] - Workforce count mentioned (e.g. 24)
 * @property {string} [remarks] - Additional field engineer remarks
 * @property {string} timestamp - ISO Timestamp of extraction
 */

/**
 * @typedef {Object} VoiceTranscriptSegment
 * @property {number} startTime - Start time in seconds
 * @property {number} endTime - End time in seconds
 * @property {string} speaker - Identified speaker (e.g. 'Er. Rajesh Sharma (Site Supervisor)')
 * @property {string} text - Transcribed spoken text
 * @property {string[]} [keyTerms] - Extracted technical terms highlighted
 */

export {};
