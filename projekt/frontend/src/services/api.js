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

  if (contentType.includes("application/pdf")) {
    return res.blob();
  }
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res.text();
}

export async function submitApplicationData(data, signal) {
  return request("/api/create_job", {
    method: "POST",
    body: data,
    signal
  });
}