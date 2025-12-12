import { useState, useCallback } from "react";

/**
 * Custom hook for managing expandable/collapsible state for multiple items.
 *
 * Useful for accordions, collapsible sections, or any UI where items can be
 * toggled independently.
 *
 * @returns {Object} Object with expanded state and toggle function
 * @returns {Object} expanded - Object mapping item IDs to boolean expanded state
 * @returns {Function} toggleExpanded - Function to toggle expansion for a specific item
 *
 * @example
 * const { expanded, toggleExpanded } = useExpandable();
 *
 * // Toggle expansion for item with ID "item-1"
 * <button onClick={() => toggleExpanded("item-1")}>
 *   {expanded["item-1"] ? "Collapse" : "Expand"}
 * </button>
 */
export function useExpandable() {
  const [expanded, setExpanded] = useState({});

  const toggleExpanded = useCallback((id) => {
    setExpanded((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  }, []);

  return { expanded, toggleExpanded };
}
