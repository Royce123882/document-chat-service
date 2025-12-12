import PropTypes from "prop-types";
import { formatRelevanceScore } from "../../utils/format";
import "./ChunkDisplay.css";

/**
 * Displays document chunks with relevance scores and metadata.
 *
 * Shows the relevant sections of a document that were retrieved to answer
 * a user's question, including content, page numbers, and relevance scores.
 */
function ChunkDisplay({ chunks, isExpanded, onToggle, chunksCount }) {
  return (
    <div className="chunks-section">
      <button className="chunks-toggle" onClick={onToggle}>
        <span className="material-icon icon-sm">description</span>
        <span>
          Found {chunksCount} relevant section{chunksCount !== 1 ? "s" : ""}
        </span>
        <span
          className={`material-icon icon-sm chevron ${isExpanded ? "expanded" : ""}`}
        >
          expand_more
        </span>
      </button>

      {isExpanded && chunks && chunks.length > 0 && (
        <div className="chunks-content">
          {chunks.map((chunk, index) => (
            <div key={index} className="chunk-item">
              <div className="chunk-header">
                <span className="chunk-number">Section {index + 1}</span>
                {chunk.metadata?.page !== undefined && (
                  <span className="chunk-page">Page {chunk.metadata.page}</span>
                )}
              </div>
              <div className="chunk-text">{chunk.content}</div>
              {chunk.score !== undefined && (
                <div className="chunk-similarity">
                  Relevance: {formatRelevanceScore(chunk.score)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

ChunkDisplay.propTypes = {
  chunks: PropTypes.arrayOf(
    PropTypes.shape({
      content: PropTypes.string.isRequired,
      score: PropTypes.number,
      metadata: PropTypes.object,
    }),
  ).isRequired,
  isExpanded: PropTypes.bool.isRequired,
  onToggle: PropTypes.func.isRequired,
  chunksCount: PropTypes.number.isRequired,
};

export default ChunkDisplay;
