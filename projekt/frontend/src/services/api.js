const API_ENDPOINT = '/api/create_job';

export const submitApplicationData = async (data) => {
  console.log(`Sende JSON an ${API_ENDPOINT}...`);

  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, application/pdf',
      },
      body: JSON.stringify(data),
    });

    console.log("Antwort vom Backend erhalten. Status:", response.status);
    console.log("Content-Type:", response.headers.get('content-type'));

    if (!response.ok) {
      let errorDetails = "Unbekannter Fehler";

      // Verbessertes Error Handling
      const contentType = response.headers.get('content-type');

      try {
        if (contentType && contentType.includes('application/json')) {
          const errorJson = await response.json();
          errorDetails = errorJson.message || errorJson.error || JSON.stringify(errorJson);
        } else {
          // Versuche Text zu lesen
          const errorText = await response.text();
          if (errorText && errorText.trim()) {
            errorDetails = `HTTP ${response.status}: ${errorText.substring(0, 300)}`;
          } else {
            errorDetails = `HTTP ${response.status}: ${response.statusText}`;
          }
        }
      } catch (readError) {
        console.error('Fehler beim Lesen der Error-Response:', readError);
        errorDetails = `HTTP ${response.status}: ${response.statusText} (Response nicht lesbar)`;
      }

      throw new Error(`Backend-Fehler: ${errorDetails}`);
    }

    // Success-Handling
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/pdf')) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      // Automatischer Download
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;

      const disposition = response.headers.get('content-disposition');
      const fileNameMatch = disposition && disposition.match(/filename="(.+)"/);
      const fileName = fileNameMatch ? fileNameMatch[1] : 'job-results.pdf';
      a.download = fileName;

      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();

      return { success: true, message: "PDF wurde erfolgreich heruntergeladen." };
    } else if (contentType && contentType.includes('application/json')) {
      const result = await response.json();
      return result;
    } else {
      return { success: true, message: "Daten erfolgreich verarbeitet." };
    }

  } catch (error) {
    console.error("Detaillierter Fehler in submitApplicationData:", error);

    // Noch spezifischere Fehlermeldungen
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Netzwerkfehler: Kann nicht mit dem Server verbinden. Ist der Server gestartet?");
    } else if (error.message.includes('Backend-Fehler')) {
      throw error; // Re-throw Backend-Fehler wie sie sind
    } else {
      throw new Error(`Client-Fehler: ${error.message}`);
    }
  }
};