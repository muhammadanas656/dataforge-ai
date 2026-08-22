/**
 * DataForge AI API Client & Endpoint Config
 * Resolves API URL with priority:
 * 1. User-customized URL saved in localStorage (e.g. deployed backend URL)
 * 2. NEXT_PUBLIC_API_URL environment variable (configured in Vercel / CI)
 * 3. Default fallback: http://localhost:8000
 */

export function getApiUrl() {
  if (typeof window !== "undefined") {
    const custom = localStorage.getItem("dataforge_custom_api_url");
    if (custom && custom.trim()) {
      return custom.trim().replace(/\/$/, "");
    }
  }
  return (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");
}

export function setCustomApiUrl(url) {
  if (typeof window !== "undefined") {
    if (url && url.trim()) {
      localStorage.setItem("dataforge_custom_api_url", url.trim().replace(/\/$/, ""));
    } else {
      localStorage.removeItem("dataforge_custom_api_url");
    }
  }
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${getApiUrl()}/api/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error(`Upload failed: ${res.statusText}`);
  }
  return res.json();
}

export async function runStage(did, stage) {
  const res = await fetch(`${getApiUrl()}/api/${stage}/${did}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Stage ${stage} failed: ${res.statusText}`);
  }
  return res.json();
}

export async function getTokens(did) {
  const url = did ? `${getApiUrl()}/api/tokens?run_id=${did}` : `${getApiUrl()}/api/tokens`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Fetch tokens failed: ${res.statusText}`);
  }
  return res.json();
}
