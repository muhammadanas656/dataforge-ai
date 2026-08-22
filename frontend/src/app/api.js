/**
 * DataForge AI API Client & BYOK (Bring-Your-Own-Key) Manager
 *
 * Privacy & Security Architecture:
 * - Each user's API Key and provider choices remain in their own browser (localStorage).
 * - Keys are NEVER hardcoded into public frontend builds or exposed to other users.
 * - All backend requests seamlessly pass 'X-API-Key', 'X-API-Provider', 'X-API-Model'
 *   headers for per-request isolated inference.
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

export function getUserCredentials() {
  if (typeof window === "undefined") {
    return { provider: "groq", api_key: "", model: "openai/gpt-oss-20b" };
  }
  return {
    provider: localStorage.getItem("dataforge_user_provider") || "groq",
    api_key: localStorage.getItem("dataforge_user_api_key") || "",
    model: localStorage.getItem("dataforge_user_model") || "openai/gpt-oss-20b",
  };
}

export function setUserCredentials({ provider, api_key, model }) {
  if (typeof window !== "undefined") {
    if (provider) localStorage.setItem("dataforge_user_provider", provider);
    if (api_key !== undefined) localStorage.setItem("dataforge_user_api_key", api_key);
    if (model) localStorage.setItem("dataforge_user_model", model);
  }
}

export function clearUserCredentials() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("dataforge_user_api_key");
  }
}

/**
 * Standard Authenticated Fetch that attaches BYOK credentials to headers
 */
export async function authFetch(input, init = {}) {
  const url = typeof input === "string" && !input.startsWith("http")
    ? `${getApiUrl()}${input.startsWith("/") ? "" : "/"}${input}`
    : input;

  const creds = getUserCredentials();
  const headers = new Headers(init.headers || {});

  if (creds.api_key) {
    headers.set("X-API-Key", creds.api_key);
  }
  if (creds.provider) {
    headers.set("X-API-Provider", creds.provider);
  }
  if (creds.model) {
    headers.set("X-API-Model", creds.model);
  }

  return fetch(url, {
    ...init,
    headers,
  });
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await authFetch(`/api/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error(`Upload failed: ${res.statusText}`);
  }
  return res.json();
}

export async function runStage(did, stage) {
  const res = await authFetch(`/api/stage/${stage}/${did}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Stage ${stage} failed: ${res.statusText}`);
  }
  return res.json();
}

export async function getTokens(did) {
  const url = did ? `/api/tokens?run_id=${did}` : `/api/tokens`;
  const res = await authFetch(url);
  if (!res.ok) {
    throw new Error(`Fetch tokens failed: ${res.statusText}`);
  }
  return res.json();
}
