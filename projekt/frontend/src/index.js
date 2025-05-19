import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./App.css";

// Stelle sicher, dass dieser Pfad korrekt ist (KEIN legacy, basierend auf deinem Bild)
import { GlobalWorkerOptions } from "pdfjs-dist/build/pdf";

// Setze den Worker-Pfad auf die LOKALE Kopie im public-Ordner
GlobalWorkerOptions.workerSrc = `/pdf.worker.min.mjs`; // Korrekter Dateiname aus public

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
