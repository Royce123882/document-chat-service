/**
 * File validation utilities.
 */

// Supported file types and extensions
const VALID_MIME_TYPES = [
  "text/plain",
  "text/markdown",
  "application/txt",
  "application/pdf",
];
const VALID_EXTENSIONS = /\.(txt|md|text|pdf)$/i;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

/**
 * Validate a file for upload.
 *
 * Checks file type and size against allowed values.
 *
 * @param {File} file - File object to validate
 * @returns {Object} Validation result with isValid flag and optional error message
 * @returns {boolean} isValid - Whether the file passed validation
 * @returns {string|null} error - Error message if validation failed, null otherwise
 *
 * @example
 * const { isValid, error } = validateFile(file);
 * if (!isValid) {
 *   console.error(error);
 * }
 */
export function validateFile(file) {
  if (!file) {
    return { isValid: false, error: "No file provided" };
  }

  // Check file type
  const isValidType =
    VALID_MIME_TYPES.includes(file.type) || VALID_EXTENSIONS.test(file.name);

  if (!isValidType) {
    return {
      isValid: false,
      error: "Please upload a text file (.txt, .md) or PDF file (.pdf)",
    };
  }

  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    return {
      isValid: false,
      error: "File size must be less than 10MB",
    };
  }

  return { isValid: true, error: null };
}
