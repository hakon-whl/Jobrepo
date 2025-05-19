// Stelle sicher, dass dieser Pfad korrekt ist (KEIN legacy)
// UND dass KEINE GlobalWorkerOptions hier importiert oder gesetzt werden!
import * as pdfjsLib from "pdfjs-dist/build/pdf";

export async function extractTextFromPdfBlob(pdfBlob) {
  const arrayBuffer =
    pdfBlob instanceof ArrayBuffer ? pdfBlob : await pdfBlob.arrayBuffer();

  // pdfjsLib wird hier verwendet - es sollte die globale Konfiguration aus index.js nutzen
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

  let text = "";
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const pageText = content.items.map((item) => item.str).join(" ");
    text += pageText + "\n--- Seite Ende ---\n";
  }
  return text;
}
