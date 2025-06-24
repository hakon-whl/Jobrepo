import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./App.css";

/**
 * PDF.js Worker-Konfiguration
 * Erforderlich für die PDF-Textextraktion
 */
const setPdfWorker = () => {
  try {
    // Dynamischer Import der PDF.js GlobalWorkerOptions
    import('pdfjs-dist/build/pdf').then((pdfjsLib) => {
      // Verschiedene Worker-Pfade für unterschiedliche Deployment-Szenarien
      const possibleWorkerPaths = [
        '/pdf.worker.min.mjs',
        '/pdf.worker.mjs',
        '/pdf.worker.min.js',
        '/pdf.worker.js',
        'https://unpkg.com/pdfjs-dist@4.0.379/build/pdf.worker.min.mjs'
      ];

      // Setze den Worker-Pfad (erster Pfad wird verwendet)
      pdfjsLib.GlobalWorkerOptions.workerSrc = possibleWorkerPaths[0];
      console.log('PDF.js Worker konfiguriert:', pdfjsLib.GlobalWorkerOptions.workerSrc);
    }).catch(err => {
      console.error('Fehler beim Konfigurieren des PDF.js Workers:', err);
    });
  } catch (error) {
    console.error('PDF.js Worker konnte nicht konfiguriert werden:', error);
  }
};

// Worker-Konfiguration vor App-Start
setPdfWorker();

// React App rendern
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);