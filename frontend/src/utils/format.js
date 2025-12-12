/**
 * Formatting utility functions for consistent data display.
 */

/**
 * Format a Date object as a human-readable timestamp.
 *
 * @param {Date} date - Date object to format
 * @returns {string} Formatted time string (e.g., "2:30 PM")
 *
 * @example
 * formatTimestamp(new Date()) // "2:30 PM"
 */
export function formatTimestamp(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/**
 * Format a file size in bytes to a human-readable string.
 *
 * @param {number} bytes - File size in bytes
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted file size (e.g., "1.5 MB")
 *
 * @example
 * formatFileSize(1536000) // "1.46 MB"
 * formatFileSize(2048) // "2.00 KB"
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

/**
 * Format a relevance score as a percentage.
 *
 * @param {number} score - Score between 0 and 1
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage (e.g., "85.3%")
 *
 * @example
 * formatRelevanceScore(0.853) // "85.3%"
 */
export function formatRelevanceScore(score, decimals = 1) {
  return `${(score * 100).toFixed(decimals)}%`;
}
