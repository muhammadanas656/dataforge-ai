export async function apiFetch(path, options = {}) {
  const workspace = typeof window !== "undefined" ? (localStorage.getItem("dataforge_workspace") || "default") : "default";
  const headers = {
    ...(options.headers || {}),
    "X-Workspace-Id": workspace,
  };
  if (options.body && typeof options.body === "string" && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  return fetch(`http://localhost:8000${path}`, { ...options, headers });
}
