import type { components } from "../generated/backend-types";

export type HealthApiResponse = components["schemas"]["HealthApiResponse"];
export type HealthResponse = components["schemas"]["HealthResponse"];
export type HealthStatus = components["schemas"]["HealthStatus"];
export type ProviderHealth = components["schemas"]["ProviderHealth"];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchHealth(signal?: AbortSignal): Promise<HealthApiResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
    headers: {
      Accept: "application/json",
    },
    signal,
  });

  const payload = (await response.json()) as HealthApiResponse;

  if (!response.ok || !payload.success || payload.data === null) {
    throw new Error(payload.error?.message ?? "Backend health check failed.");
  }

  return payload;
}
