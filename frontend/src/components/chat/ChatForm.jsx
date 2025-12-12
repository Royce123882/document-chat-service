import { forwardRef } from "react";
import PropTypes from "prop-types";
import "./ChatForm.css";

/**
 * Chat input form for sending messages.
 *
 * A controlled input component with submit button, disabled state during
 * loading, and auto-focus support.
 */
const ChatForm = forwardRef(function ChatForm(
  { value, onChange, onSubmit, loading, disabled },
  ref,
) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!value.trim() || loading || disabled) return;
    onSubmit();
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        ref={ref}
        type="text"
        className="chat-input"
        placeholder="Ask a question about your document..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={loading || disabled}
      />
      <button
        type="submit"
        className="send-button"
        disabled={!value.trim() || loading || disabled}
      >
        <span className="material-icon icon-md">send</span>
      </button>
    </form>
  );
});

ChatForm.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  disabled: PropTypes.bool,
};

ChatForm.defaultProps = {
  loading: false,
  disabled: false,
};

export default ChatForm;
