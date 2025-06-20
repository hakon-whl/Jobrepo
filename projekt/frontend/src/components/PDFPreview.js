import React, { useState, useEffect } from 'react';
import * as pdfjsLib from 'pdfjs-dist/build/pdf';

const PDFPreview = ({ file }) => {
  const [thumbnail, setThumbnail] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const generateThumbnail = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        const page = await pdf.getPage(1);

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        const viewport = page.getViewport({ scale: 0.3 });

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        await page.render({ canvasContext: context, viewport }).promise;
        setThumbnail(canvas.toDataURL());
      } catch (err) {
        console.error('Fehler beim Generieren des PDF-Thumbnails:', err);
        setError('Vorschau konnte nicht generiert werden');
      } finally {
        setIsLoading(false);
      }
    };

    if (file) {
      generateThumbnail();
    }
  }, [file]);

  if (isLoading) {
    return <div className="pdf-thumbnail-loading">Lade Vorschau...</div>;
  }

  if (error) {
    return <div className="pdf-thumbnail-error">⚠️ {error}</div>;
  }

  return thumbnail ? (
    <div className="pdf-thumbnail-container">
      <img src={thumbnail} alt={`PDF Preview: ${file.name}`} className="pdf-thumbnail" />
      <div className="pdf-thumbnail-overlay">
        <span className="pdf-filename">{file.name}</span>
      </div>
    </div>
  ) : null;
};

export default PDFPreview;