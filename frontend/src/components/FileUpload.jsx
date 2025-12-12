import { useState } from "react";
import PropTypes from "prop-types";
import { documentService } from "../services/api";
import { useApiCall } from "../hooks";
import { validateFile } from "../utils/validation";
import DropZone from "./upload/DropZone";
import "./FileUpload.css";

/**
 * Drag-and-drop upload card that validates files locally before calling the backend.
 *
 * Features:
 * - Drag and drop or click to browse file selection
 * - Client-side validation for file type and size
 * - Visual upload progress with loading states
 * - Error handling with user-friendly messages
 */
function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const { loading: uploading, error, execute, setError } = useApiCall();

  /**
   * Validate and set the selected file.
   * Clears any previous errors if validation passes.
   */
  const handleFileSelect = (selectedFile) => {
    const { isValid, error: validationError } = validateFile(selectedFile);

    if (!isValid) {
      setError(validationError);
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  /**
   * Remove the selected file and clear any errors.
   */
  const handleFileRemove = () => {
    setFile(null);
    setError(null);
  };

  /**
   * Upload the file to the backend.
   * Validates that a file is selected before uploading.
   */
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    const response = await execute(
      () => documentService.uploadDocument(file),
      "Failed to upload document. Please try again.",
    );

    if (response) {
      onUploadSuccess(response);
    }
  };

  /**
   * Drag and drop event handlers.
   */
  const dragHandlers = {
    onDragEnter: (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(true);
    },
    onDragLeave: (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
    },
    onDragOver: (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(true);
    },
    onDrop: (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    },
  };

  return (
    <div className="file-upload-container">
      <div className="upload-card">
        <h2>Upload Your Document</h2>
        <p className="upload-description">
          Got a text or PDF? Upload it and ask anything about it.
        </p>

        <DropZone
          file={file}
          onFileSelect={handleFileSelect}
          onFileRemove={handleFileRemove}
          dragActive={dragActive}
          onDragHandlers={dragHandlers}
        />

        {error && (
          <div className="error-message">
            <span className="material-icon icon-sm">error</span>
            {error}
          </div>
        )}

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? (
            <>
              <span className="spinner"></span>
              Uploading...
            </>
          ) : (
            "Upload & Start Chatting"
          )}
        </button>
      </div>
    </div>
  );
}

FileUpload.propTypes = {
  onUploadSuccess: PropTypes.func.isRequired,
};

export default FileUpload;
