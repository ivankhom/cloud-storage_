const API_BASE = import.meta.env.VITE_API_BASE || "";

function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

async function ensureCsrf() {
  if (!getCookie("csrftoken")) {
    await fetch(`${API_BASE}/api/users/csrf/`, { credentials: "include" });
  }
}

async function request(path, { method = "GET", body, isForm = false } = {}) {
  if (method !== "GET") {
    await ensureCsrf();
  }
  const headers = {};
  const csrf = getCookie("csrftoken");
  if (csrf && method !== "GET") headers["X-CSRFToken"] = csrf;
  if (!isForm && body !== undefined) headers["Content-Type"] = "application/json";

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: "include",
    headers,
    body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
  });

  let data = null;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    data = await response.json();
  }

  if (!response.ok) {
    const error = new Error((data && data.error) || `Ошибка запроса (${response.status})`);
    error.details = data && data.details;
    error.status = response.status;
    throw error;
  }
  return data;
}

export const api = {
  csrf: () => ensureCsrf(),
  register: (payload) => request("/api/users/register/", { method: "POST", body: payload }),
  login: (payload) => request("/api/users/login/", { method: "POST", body: payload }),
  logout: () => request("/api/users/logout/", { method: "POST" }),
  me: () => request("/api/users/me/"),

  userList: () => request("/api/users/"),
  userDelete: (id) => request(`/api/users/${id}/`, { method: "DELETE" }),
  userSetAdmin: (id, isAdmin) =>
    request(`/api/users/${id}/admin/`, { method: "PATCH", body: { is_admin: isAdmin } }),

  fileList: (userId) => request(`/api/files/${userId ? `?user=${userId}` : ""}`),
  fileUpload: (file, comment, userId) => {
    const form = new FormData();
    form.append("file", file);
    form.append("comment", comment || "");
    if (userId) form.append("user", userId);
    return request("/api/files/upload/", { method: "POST", body: form, isForm: true });
  },
  fileDelete: (id) => request(`/api/files/${id}/`, { method: "DELETE" }),
  fileRename: (id, name) => request(`/api/files/${id}/rename/`, { method: "PATCH", body: { name } }),
  fileComment: (id, comment) =>
    request(`/api/files/${id}/comment/`, { method: "PATCH", body: { comment } }),
  fileRegenerateLink: (id) => request(`/api/files/${id}/link/`, { method: "POST" }),
  fileDownloadUrl: (id) => `${API_BASE}/api/files/${id}/download/`,
  filePublicUrl: (token) => `${window.location.origin}${API_BASE}/api/public/${token}/`,
};

export default api;
