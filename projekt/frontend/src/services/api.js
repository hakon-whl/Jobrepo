// API-Basis-URL aus Umgebungsvariablen oder Fallback auf leeren String
const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

/**
 * Generische HTTP-Request-Funktion
 * Behandelt JSON- und PDF-Responses sowie Fehlerbehandlung
 *
 * @param {string} path - API-Endpunkt-Pfad
 * @param {Object} options - Request-Optionen
 * @returns {Promise} Response-Daten als JSON, Blob oder Text
 */
async function request(path, {
  method = "GET",
  body = null,
  headers = {},
  signal = null
} = {}) {
  const url = `${API_BASE}${path}`;
  const init = {
    method,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, application/pdf",
      ...headers
    },
    signal
  };

  // Body nur bei nicht-GET Requests hinzufügen
  if (body !== null) init.body = JSON.stringify(body);

  const res = await fetch(url, init);
  const contentType = res.headers.get("content-type") || "";

  // Fehlerbehandlung mit verbesserter Fehlermeldung
  if (!res.ok) {
    let detail;
    try {
      if (contentType.includes("application/json")) {
        const json = await res.json();
        detail = json.message || JSON.stringify(json);
      } else {
        detail = await res.text() || res.statusText;
      }
    } catch {
      detail = res.statusText;
    }
    throw new Error(`API-Fehler ${res.status}: ${detail}`);
  }

  // Response-Typ-basierte Rückgabe
  if (contentType.includes("application/pdf")) {
    return res.blob();
  }
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res.text();
}

/**
 * Sendet Bewerbungsdaten an die API
 *
 * @param {Object} data - Bewerbungsdaten inklusive PDF-Inhalte
 * @param {AbortSignal} signal - Optional: AbortController-Signal für Request-Abbruch
 * @returns {Promise} API-Response
 */
export async function submitApplicationData(data, signal) {
  return request("/api/create_job", {
    method: "POST",
    body: data,
    signal
  });
}