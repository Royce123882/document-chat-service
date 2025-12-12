import PropTypes from "prop-types";
import { formatTimestamp } from "../../utils/format";
import ChunkDisplay from "./ChunkDisplay";
import "./Message.css";

/**
 * System message component for informational messages.
 */
function SystemMessage({ content }) {
  return (
    <div className="message message-system">
      <div className="message-content system-message">{content}</div>
    </div>
  );
}

SystemMessage.propTypes = {
  content: PropTypes.string.isRequired,
};

/**
 * User message component with timestamp.
 */
function UserMessage({ content, timestamp }) {
  return (
    <div className="message message-user">
      <div className="message-bubble user-bubble">
        <div className="message-content">{content}</div>
      </div>
      <div className="message-time user-time">{formatTimestamp(timestamp)}</div>
    </div>
  );
}

UserMessage.propTypes = {
  content: PropTypes.string.isRequired,
  timestamp: PropTypes.instanceOf(Date).isRequired,
};

/**
 * Assistant message component with optional chunks display.
 */
function AssistantMessage({
  content,
  timestamp,
  chunks,
  chunksFound,
  isChunksExpanded,
  onToggleChunks,
}) {
  return (
    <div className="message message-assistant">
      <div className="message-bubble assistant-bubble">
        <div className="message-content-wrapper">
          <div className="message-content">{content}</div>
          {chunksFound > 0 && (
            <ChunkDisplay
              chunks={chunks}
              isExpanded={isChunksExpanded}
              onToggle={onToggleChunks}
              chunksCount={chunksFound}
            />
          )}
        </div>
      </div>
      <div className="message-time assistant-time">
        {formatTimestamp(timestamp)}
      </div>
    </div>
  );
}

AssistantMessage.propTypes = {
  content: PropTypes.string.isRequired,
  timestamp: PropTypes.instanceOf(Date).isRequired,
  chunks: PropTypes.array,
  chunksFound: PropTypes.number,
  isChunksExpanded: PropTypes.bool.isRequired,
  onToggleChunks: PropTypes.func.isRequired,
};

AssistantMessage.defaultProps = {
  chunks: [],
  chunksFound: 0,
};

/**
 * Error message component.
 */
function ErrorMessage({ content }) {
  return (
    <div className="message message-error">
      <div className="message-content error-message">
        <span className="material-icon icon-sm">error</span>
        {content}
      </div>
    </div>
  );
}

ErrorMessage.propTypes = {
  content: PropTypes.string.isRequired,
};

/**
 * Loading indicator for assistant messages.
 */
function TypingIndicator() {
  return (
    <div className="message message-assistant">
      <div className="message-bubble assistant-bubble">
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
}

/**
 * Generic message component that renders the appropriate message type.
 */
function Message({ message, messageIndex, expandedChunks, onToggleChunks }) {
  const { type } = message;

  if (type === "system") {
    return <SystemMessage content={message.content} />;
  }

  if (type === "user") {
    return (
      <UserMessage content={message.content} timestamp={message.timestamp} />
    );
  }

  if (type === "assistant") {
    return (
      <AssistantMessage
        content={message.content}
        timestamp={message.timestamp}
        chunks={message.chunks}
        chunksFound={message.chunks_found}
        isChunksExpanded={expandedChunks[messageIndex] || false}
        onToggleChunks={() => onToggleChunks(messageIndex)}
      />
    );
  }

  if (type === "error") {
    return <ErrorMessage content={message.content} />;
  }

  return null;
}

Message.propTypes = {
  message: PropTypes.shape({
    type: PropTypes.oneOf(["system", "user", "assistant", "error"]).isRequired,
    content: PropTypes.string.isRequired,
    timestamp: PropTypes.instanceOf(Date),
    chunks: PropTypes.array,
    chunks_found: PropTypes.number,
  }).isRequired,
  messageIndex: PropTypes.number.isRequired,
  expandedChunks: PropTypes.object.isRequired,
  onToggleChunks: PropTypes.func.isRequired,
};

export default Message;
export {
  SystemMessage,
  UserMessage,
  AssistantMessage,
  ErrorMessage,
  TypingIndicator,
};
