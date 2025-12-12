import { useState } from "react";
import FileUpload from "./components/FileUpload";
import ChatInterface from "./components/ChatInterface";
import "./App.css";

/**
 * Root component that toggles between upload and chat workflows based on collection state.
 */
function App() {
  const [collectionId, setCollectionId] = useState(null);
  const [documentName, setDocumentName] = useState("");

  const handleUploadSuccess = (uploadDetails) => {
    setCollectionId(uploadDetails.collection_id);
    setDocumentName(uploadDetails.document_name);
  };

  const handleNewDocument = () => {
    setCollectionId(null);
    setDocumentName("");
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Document Chat Service</h1>
        <p>Powered by SAP Document Grounding Service</p>
      </header>

      <main className="app-main">
        {!collectionId ? (
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        ) : (
          <ChatInterface
            collectionId={collectionId}
            documentName={documentName}
            onNewDocument={handleNewDocument}
          />
        )}
      </main>
    </div>
  );
}

export default App;
