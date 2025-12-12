import { useState } from "react";
import PropTypes from "prop-types";
import "./LLMSettings.css";

/**
 * LLM configuration component for customizing model parameters.
 *
 * Allows users to adjust:
 * - Model selection (GPT-4o, GPT-5, etc.)
 * - Temperature (creativity vs. focus)
 * - Max tokens (response length)
 */
function LLMSettings({ settings, onSettingsChange }) {
  const [isExpanded, setIsExpanded] = useState(false);

  /**
   * Generic handler factory for updating settings.
   * Reduces code duplication for similar change handlers.
   *
   * @param {string} key - The settings key to update
   * @param {Function} transformer - Optional function to transform the value
   */
  const createSettingHandler =
    (key, transformer = (v) => v) =>
    (e) => {
      onSettingsChange({ ...settings, [key]: transformer(e.target.value) });
    };

  const handleModelChange = createSettingHandler("llm_model");
  const handleTemperatureChange = createSettingHandler(
    "llm_temperature",
    parseFloat,
  );
  const handleMaxTokensChange = createSettingHandler(
    "llm_max_tokens",
    parseInt,
  );

  const resetToDefaults = () => {
    onSettingsChange({
      llm_model: "gpt-4o",
      llm_temperature: 0.7,
      llm_max_tokens: 10000,
    });
  };

  return (
    <div className="llm-settings">
      <button
        className="settings-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        type="button"
      >
        <span className="material-icon icon-sm">settings</span>
        <span>LLM Settings</span>
        <span
          className={`material-icon icon-sm chevron ${isExpanded ? "expanded" : ""}`}
        >
          expand_more
        </span>
      </button>

      {isExpanded && (
        <div className="settings-panel">
          <div className="setting-group">
            <label htmlFor="llm-model">
              Model
              <span
                className="setting-info"
                title="The LLM model to use for generating responses"
              >
                ⓘ
              </span>
            </label>
            <select
              id="llm-model"
              value={settings.llm_model}
              onChange={handleModelChange}
              className="setting-select"
            >
              <option value="gpt-4o">GPT-4o (Recommended)</option>
              <option value="gpt-5">GPT-5</option>
            </select>
          </div>

          <div className="setting-group">
            <label htmlFor="llm-temperature">
              Temperature: {settings.llm_temperature.toFixed(2)}
              <span
                className="setting-info"
                title="Controls randomness. Lower = more focused, Higher = more creative"
              >
                ⓘ
              </span>
            </label>
            <input
              id="llm-temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={settings.llm_temperature}
              onChange={handleTemperatureChange}
              className="setting-slider"
            />
            <div className="slider-labels">
              <span>Focused (0.0)</span>
              <span>Creative (2.0)</span>
            </div>
          </div>

          <div className="setting-group">
            <label htmlFor="llm-max-tokens">
              Max Tokens: {settings.llm_max_tokens}
              <span
                className="setting-info"
                title="Maximum length of the response"
              >
                ⓘ
              </span>
            </label>
            <input
              id="llm-max-tokens"
              type="range"
              min="100"
              max="16000"
              step="100"
              value={settings.llm_max_tokens}
              onChange={handleMaxTokensChange}
              className="setting-slider"
            />
            <div className="slider-labels">
              <span>Short (100)</span>
              <span>Long (16000)</span>
            </div>
          </div>

          <button
            className="reset-button"
            onClick={resetToDefaults}
            type="button"
          >
            Reset to Defaults
          </button>
        </div>
      )}
    </div>
  );
}

LLMSettings.propTypes = {
  settings: PropTypes.shape({
    llm_model: PropTypes.string.isRequired,
    llm_temperature: PropTypes.number.isRequired,
    llm_max_tokens: PropTypes.number.isRequired,
  }).isRequired,
  onSettingsChange: PropTypes.func.isRequired,
};

export default LLMSettings;
