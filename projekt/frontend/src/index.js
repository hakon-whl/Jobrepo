import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./App.css";

// PDF.js Worker-Konfiguration OHNE Import der GlobalWorkerOptions
// Der Worker-Pfad muss auf die tatsächlich verfügbare Datei zeigen
const setPdfWorker = () => {
  try {
    // Dynamischer Import der GlobalWorkerOptions zur Laufzeit
    import('pdfjs-dist/build/pdf').then((pdfjsLib) => {
      // Prüfe verschiedene mögliche Worker-Pfade
      const possibleWorkerPaths = [
        '/pdf.worker.min.mjs',
        '/pdf.worker.mjs',
        '/pdf.worker.min.js',
        '/pdf.worker.js',
        'https://unpkg.com/pdfjs-dist@4.0.379/build/pdf.worker.min.mjs'
      ];

      // Verwende den ersten verfügbaren Pfad
      pdfjsLib.GlobalWorkerOptions.workerSrc = possibleWorkerPaths[0];
      console.log('PDF.js Worker konfiguriert:', pdfjsLib.GlobalWorkerOptions.workerSrc);
    }).catch(err => {
      console.error('Fehler beim Konfigurieren des PDF.js Workers:', err);
    });
  } catch (error) {
    console.error('PDF.js Worker konnte nicht konfiguriert werden:', error);
  }
};

setPdfWorker();

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);