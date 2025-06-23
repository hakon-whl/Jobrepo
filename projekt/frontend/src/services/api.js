const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

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
  if (body !== null) init.body = JSON.stringify(body);

  const res = await fetch(url, init);
  const contentType = res.headers.get("content-type") || "";

  if (!res.ok) {
    // verbessertes Error-Parsing
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

  // Success: je nach Content-Type
  if (contentType.includes("application/pdf")) {
    return res.blob();
  }
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res.text();
}

export async function submitApplicationData(data, signal) {
  const result = await request("/api/create_job", {
    method: "POST",
    body: data,
    signal
  });

  // Wenn wir ein Blob bekommen: PDF-Download anstoßen
  if (result instanceof Blob) {
    const url = URL.createObjectURL(result);
    const a = document.createElement("a");
    a.href = url;

    // optionaler Dateiname aus Content-Disposition
    const disposition = result.type === "application/pdf"
      ? (new RegExp('filename="(.+)"')
          .exec(a.download) || [])[1]
      : null;
    a.download = disposition || "job-results.pdf";

    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    return { success: true, message: "PDF wurde erfolgreich heruntergeladen." };
  }

  // JSON-Antwort direkt zurückliefern
  return result;
}