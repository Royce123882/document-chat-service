import { useRef, useEffect } from "react";
import PropTypes from "prop-types";
import Message from "./Message";
import { TypingIndicator } from "./Message";
import "./MessageList.css";

/**
 * Container for displaying a list of chat messages with auto-scroll.
 *
 * Handles rendering all message types (system, user, assistant, error)
 * and displays a loading indicator when waiting for a response.
 */
function MessageList({ messages, loading, expandedChunks, onToggleChunks }) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="messages-container">
      <div className="messages">
        {messages.map((message, index) => (
          <Message
            key={index}
            message={message}
            messageIndex={index}
            expandedChunks={expandedChunks}
            onToggleChunks={onToggleChunks}
          />
        ))}

        {loading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

MessageList.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.oneOf(["system", "user", "assistant", "error"])
        .isRequired,
      content: PropTypes.string.isRequired,
      timestamp: PropTypes.instanceOf(Date),
      chunks: PropTypes.array,
      chunks_found: PropTypes.number,
    }),
  ).isRequired,
  loading: PropTypes.bool,
  expandedChunks: PropTypes.object.isRequired,
  onToggleChunks: PropTypes.func.isRequired,
};

MessageList.defaultProps = {
  loading: false,
};

export default MessageList;
