import { getApiAccessToken } from "./auth";

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"
).replace(/\/$/, "");

function buildUrl(path) {
  return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  if (response.status === 204) {
    return null;
  }

  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

function messageFromPayload(payload, fallback) {
  if (!payload) {
    return fallback;
  }

  if (typeof payload === "string") {
    return payload || fallback;
  }

  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((item) => item?.msg || item?.message || item)
      .filter(Boolean)
      .join(" ");
  }

  return payload.detail || payload.message || payload.error || fallback;
}

async function apiRequest(path, options = {}) {
  const token = await getApiAccessToken();
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(buildUrl(path), {
    ...options,
    headers
  });
  const payload = await parseResponse(response);

  if (!response.ok) {
    throw new Error(messageFromPayload(payload, `Request failed with status ${response.status}`));
  }

  return payload;
}

export function registerUser(email, password) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export function loginUser(email, password) {
  const formData = new URLSearchParams();
  formData.set("username", email);
  formData.set("password", password);

  return apiRequest("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: formData
  });
}

export function getCurrentUser() {
  return apiRequest("/auth/me");
}

export function listDocuments() {
  return apiRequest("/documents");
}

export function uploadDocument(file) {
  const formData = new FormData();
  formData.set("file", file);

  return apiRequest("/documents/upload", {
    method: "POST",
    body: formData
  });
}

export function submitConsent(documentId, processingConsent, storageConsent) {
  return apiRequest(`/documents/${documentId}/consent`, {
    method: "POST",
    body: JSON.stringify({
      processing_consent: processingConsent,
      storage_consent: storageConsent
    })
  });
}

export function getJobStatus(documentId) {
  return apiRequest(`/jobs/${documentId}/status`);
}

export function getResults(documentId) {
  return apiRequest(`/documents/${documentId}/results`);
}

export function deleteDocument(documentId) {
  return apiRequest(`/documents/${documentId}`, {
    method: "DELETE"
  });
}

export function askDocument(documentId, question, userContext = "") {
  return apiRequest(`/documents/${documentId}/ask`, {
    method: "POST",
    body: JSON.stringify({
      question,
      user_context: userContext || null,
      top_k: 5
    })
  });
}
