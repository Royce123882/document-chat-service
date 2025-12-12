import { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";
import { documentService } from "../services/api";
import { useExpandable } from "../hooks";
import ChatHeader from "./chat/ChatHeader";
import MessageList from "./chat/MessageList";
import ChatForm from "./chat/ChatForm";
import "./ChatInterface.css";

/**
 * Conversational UI for chatting with a document collection.
 *
 * Displays document information, message history, and an input form.
 * Composed of smaller sub-components:
 * - ChatHeader: Document info and settings
 * - MessageList: Message rendering and display
 * - ChatForm: Input form for sending messages
 */
function ChatInterface({ collectionId, documentName, onNewDocument }) {
  // Message state
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");

  // API state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // UI state
  const { expanded: expandedChunks, toggleExpanded: toggleChunks } =
    useExpandable();
  const [llmSettings, setLlmSettings] = useState({
    llm_model: "gpt-4o",
    llm_temperature: 0.7,
    llm_max_tokens: 10000,
  });

  const inputRef = useRef(null);

  // Initialize welcome message when document changes
  useEffect(() => {
    setMessages([
      {
        type: "system",
        content: `Document "${documentName}" uploaded successfully. You can now ask questions about it.`,
        timestamp: new Date(),
      },
    ]);
  }, [documentName]);

  // Handle sending a new message
  const handleSubmit = async () => {
    if (!inputValue.trim() || loading) return;

    // Create and add user message
    const userMessage = {
      type: "user",
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);
    setError(null);

    try {
      // Call the API to get assistant response
      const response = await documentService.sendChatQuery(
        collectionId,
        userMessage.content,
        5, // maxChunks
        llmSettings.llm_model,
        llmSettings.llm_temperature,
        llmSettings.llm_max_tokens,
      );

      // Create and add assistant message with chunks
      const assistantMessage = {
        type: "assistant",
        content: response.response,
        chunks: response.chunks,
        chunks_found: response.chunks_found,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      // Set error state and add error message to chat
      setError(
        err.response?.data?.detail ||
          "Failed to get response. Please try again.",
      );

      const errorMessage = {
        type: "error",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="chat-interface">
      <ChatHeader
        documentName={documentName}
        collectionId={collectionId}
        llmSettings={llmSettings}
        onSettingsChange={setLlmSettings}
        onNewDocument={onNewDocument}
      />

      <MessageList
        messages={messages}
        loading={loading}
        expandedChunks={expandedChunks}
        onToggleChunks={toggleChunks}
      />

      {error && (
        <div className="chat-error">
          <span className="material-icon icon-sm">error</span>
          {error}
        </div>
      )}

      <ChatForm
        ref={inputRef}
        value={inputValue}
        onChange={setInputValue}
        onSubmit={handleSubmit}
        loading={loading}
      />
    </div>
  );
}

ChatInterface.propTypes = {
  collectionId: PropTypes.string.isRequired,
  documentName: PropTypes.string.isRequired,
  onNewDocument: PropTypes.func.isRequired,
};

export default ChatInterface;
