import { useRef } from "react";
import PropTypes from "prop-types";
import { formatFileSize } from "../../utils/format";
import "./DropZone.css";

/**
 * Drag-and-drop file selector with file preview.
 *
 * Provides a drop zone for file uploads with visual feedback for drag state.
 * Shows file info when a file is selected with an option to remove it.
 */
function DropZone({
  file,
  onFileSelect,
  onFileRemove,
  dragActive,
  onDragHandlers,
}) {
  const fileInputRef = useRef(null);

  const handleClick = () => {
    if (!file) {
      fileInputRef.current?.click();
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  return (
    <div
      className={`drop-zone ${dragActive ? "drag-active" : ""} ${file ? "has-file" : ""}`}
      onDragEnter={onDragHandlers.onDragEnter}
      onDragLeave={onDragHandlers.onDragLeave}
      onDragOver={onDragHandlers.onDragOver}
      onDrop={onDragHandlers.onDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        accept=".txt,.md,.text,.pdf"
        className="file-input"
      />

      {!file ? (
        <div className="drop-zone-empty">
          <div className="upload-icon">
            <span className="material-icon icon-xl">cloud_upload</span>
          </div>
          <p className="drop-text">
            <strong>Drop your file here</strong> or click to browse
          </p>
          <p className="file-types">Supported: .txt, .md, .pdf (max 10MB)</p>
        </div>
      ) : (
        <div className="file-info">
          <div className="file-icon">
            <span className="material-icon icon-lg">description</span>
          </div>
          <div className="file-details">
            <p className="file-name">{file.name}</p>
            <p className="file-size">{formatFileSize(file.size)}</p>
          </div>
          <button
            type="button"
            className="remove-button"
            onClick={(e) => {
              e.stopPropagation();
              onFileRemove();
            }}
            title="Remove file"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
}

DropZone.propTypes = {
  file: PropTypes.instanceOf(File),
  onFileSelect: PropTypes.func.isRequired,
  onFileRemove: PropTypes.func.isRequired,
  dragActive: PropTypes.bool.isRequired,
  onDragHandlers: PropTypes.shape({
    onDragEnter: PropTypes.func.isRequired,
    onDragLeave: PropTypes.func.isRequired,
    onDragOver: PropTypes.func.isRequired,
    onDrop: PropTypes.func.isRequired,
  }).isRequired,
};

DropZone.defaultProps = {
  file: null,
};

export default DropZone;
