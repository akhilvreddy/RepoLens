import type { ChatResponse, RepositoryAnalysis } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function analyzeRepository(url: string, forceRefresh = false, init?: RequestInit) {
  return request<RepositoryAnalysis>("/api/repositories/analyze", {
    method: "POST",
    body: JSON.stringify({ url, force_refresh: forceRefresh }),
    ...init,
  });
}

export function getRepositoryAnalysis(owner: string, repo: string) {
  return request<RepositoryAnalysis>(`/api/repositories/${owner}/${repo}`);
}

export function askRepository(owner: string, repo: string, question: string, sessionId?: number) {
  return request<ChatResponse>(`/api/repositories/${owner}/${repo}/chat`, {
    method: "POST",
    body: JSON.stringify({ question, session_id: sessionId }),
  });
}
