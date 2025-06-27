import React, { useState } from 'react';
import ApplicationForm from './components/ApplicationForm';
import { submitApplicationData } from './services/api';
import { LOCATIONS_DATA } from './constants/enums';
import { useSkills } from './hooks/useSkills';


export const extractTextFromPdfBlob = async (file) => {
  try {
    const pdfjsLib = await import('pdfjs-dist/build/pdf');
    pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://unpkg.com/pdfjs-dist@4.0.379/build/pdf.worker.min.mjs';
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
    let fullText = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      fullText += pageText + '\n';
    }
    return fullText.trim();
  } catch (error) {
    console.error('PDF-Extraktion fehlgeschlagen:', error);
    throw new Error(`PDF-Verarbeitung fehlgeschlagen: ${error.message}`);
  }
};

function App() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const { allSkills, updateSkills } = useSkills();

  /**
   * Formular-Submit: holt den PDF-Blob und löst
   * den Download per unsichtbarem <a> aus
   */
  const handleFormSubmit = async (data) => {
    setIsSubmitting(true);
    setSubmitStatus('loading');

    try {
      // Backend gibt einen Blob zurück
      const pdfBlob = await submitApplicationData(data);

      // 1. Blob → Object-URL
      const url = window.URL.createObjectURL(pdfBlob);

      // 2. unsichtbaren Link erzeugen
      const a = document.createElement('a');
      a.href = url;
      a.download = 'summary.pdf';
      document.body.appendChild(a);

      // 3. Klick auslösen
      a.click();

      // 4. Aufräumen
      a.remove();
      window.URL.revokeObjectURL(url);

      setSubmitStatus('success');
    } catch (err) {
      console.error(err);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-container">
      <h1>Bewerbungsdaten Erfassen und Senden</h1>
      <div className="content-wrapper">
        <ApplicationForm
          onSubmit={handleFormSubmit}
          isSubmitting={isSubmitting}
          locationsData={LOCATIONS_DATA}
          availableSkills={allSkills}
          onSkillsUpdate={updateSkills}
        />
        {submitStatus && (
          <p className={`status-message ${submitStatus}`}>
            {submitStatus === 'loading'
              ? 'Lädt...'
              : submitStatus === 'success'
              ? 'Erfolgreich gesendet!'
              : 'Fehler beim Senden!'}
          </p>
        )}
      </div>
    </div>
  );
}

export default App;