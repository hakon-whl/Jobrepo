const API_ENDPOINT = '/api/create_job';

export const submitApplicationData = async (data) => {
  console.log(`Sende JSON an ${API_ENDPOINT}...`);
  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, application/pdf', // Unterstützt jetzt auch PDF
      },
      body: JSON.stringify(data),
    });

    console.log("Antwort vom Backend erhalten. Status:", response.status);

    if (!response.ok) {
      let errorDetails = "Unbekannter Fehler";
      try {
        const errorJson = await response.json();
        errorDetails = errorJson.message || errorJson.error || JSON.stringify(errorJson);
      } catch (jsonError) {
        try {
          const errorText = await response.text();
          errorDetails = `HTTP Status ${response.status}: ${response.statusText}. Antwort Text (Anfang): ${errorText.substring(0, 200)}...`;
        } catch (textError) {
          errorDetails = `HTTP Status ${response.status}: ${response.statusText}. Konnte Antwort Body nicht lesen.`;
        }
      }
      throw new Error(`Backend-Fehler: ${errorDetails}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/pdf')) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      // Automatischer Download mit einem temporären Link
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;

      // Extrahiere den Dateinamen aus dem Content-Disposition Header, falls vorhanden
      const disposition = response.headers.get('content-disposition');
      const fileNameMatch = disposition && disposition.match(/filename="(.+)"/);
      const fileName = fileNameMatch ? fileNameMatch[1] : 'job-results.pdf';
      a.download = fileName;

      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();

      return { success: true, message: "PDF wurde erfolgreich heruntergeladen." };
    } else {
      // Erfolgreiche JSON-Antwort verarbeiten
      const result = await response.json();
      return result;
    }

  } catch (error) {
    console.error("Fehler in submitApplicationData beim Senden/Empfangen:", error);
    throw new Error(error.message || "Ein unbekannter Netzwerk- oder Client-Fehler ist aufgetreten.");
  }
};
