import { useState, useCallback } from "react";

/**
 * Custom hook for managing API call state (loading, error).
 *
 * Provides a clean pattern for handling async operations with loading indicators
 * and error handling. Automatically manages loading state and catches errors.
 *
 * @returns {Object} Object with loading state, error state, and execute function
 * @returns {boolean} loading - Whether an API call is currently in progress
 * @returns {string|null} error - Error message if the last call failed, null otherwise
 * @returns {Function} execute - Function to execute an async operation
 * @returns {Function} setError - Function to manually set error state
 * @returns {Function} clearError - Function to clear error state
 *
 * @example
 * const { loading, error, execute, clearError } = useApiCall();
 *
 * const handleSubmit = async () => {
 *   const result = await execute(async () => {
 *     return await api.uploadDocument(file);
 *   });
 *
 *   if (result) {
 *     console.log("Success:", result);
 *   }
 * };
 */
export function useApiCall() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (apiFunction, errorMessage = "An error occurred") => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiFunction();
        return result;
      } catch (err) {
        const message = err.response?.data?.detail || errorMessage;
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return { loading, error, execute, setError, clearError };
}
