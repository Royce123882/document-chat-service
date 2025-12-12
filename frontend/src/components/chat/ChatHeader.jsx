import PropTypes from "prop-types";
import LLMSettings from "../LLMSettings";
import "./ChatHeader.css";

/**
 * Header for the chat interface with document info and controls.
 *
 * Displays the current document name, collection ID, LLM settings panel,
 * and a button to start over with a new document.
 */
function ChatHeader({
  documentName,
  collectionId,
  llmSettings,
  onSettingsChange,
  onNewDocument,
}) {
  return (
    <div className="chat-header">
      <div className="chat-header-info">
        <h2>{documentName}</h2>
        <span className="collection-id">
          Collection: {collectionId.substring(0, 8)}...
        </span>
      </div>
      <div className="chat-header-actions">
        <LLMSettings
          settings={llmSettings}
          onSettingsChange={onSettingsChange}
        />
        <button className="new-document-button" onClick={onNewDocument}>
          <span className="material-icon icon-md">add</span>
          New Document
        </button>
      </div>
    </div>
  );
}

ChatHeader.propTypes = {
  documentName: PropTypes.string.isRequired,
  collectionId: PropTypes.string.isRequired,
  llmSettings: PropTypes.shape({
    llm_model: PropTypes.string.isRequired,
    llm_temperature: PropTypes.number.isRequired,
    llm_max_tokens: PropTypes.number.isRequired,
  }).isRequired,
  onSettingsChange: PropTypes.func.isRequired,
  onNewDocument: PropTypes.func.isRequired,
};

export default ChatHeader;
