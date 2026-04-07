import { useEffect, useState } from "react";
import {
  fetchHealth,
  type HealthApiResponse,
  type HealthResponse,
  type ProviderHealth,
} from "./api/health";

const shellCards = [
  {
    title: "Local Provider",
    description:
      "The health endpoint now reports the configured local Hugging Face provider and whether the on-disk model is reachable.",
  },
  {
    title: "Failure Visibility",
    description: "Provider errors stay visible in the health payload instead of failing silently inside the desktop shell.",
  },
  {
    title: "Current Scope",
    description: "Step 5 only connects the local provider layer. It does not add `/api/v1/chat`, routing, or tool execution.",
  },
];

function formatStatusLabel(status: HealthResponse["status"]) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatTimestamp(timestamp: string) {
  return new Date(timestamp).toLocaleString();
}

function formatLatency(latencyMs: number | null | undefined) {
  if (typeof latencyMs !== "number") {
    return "N/A";
  }

  return `${latencyMs.toFixed(2)} ms`;
}

function buildServiceEntries(services: HealthResponse["services"] | undefined) {
  return [
    {
      key: "backend",
      label: "Backend API",
      fallbackProvider: "backend",
      health: services?.backend,
    },
    {
      key: "local_llm",
      label: "Local LLM",
      fallbackProvider: "huggingface_local",
      health: services?.local_llm,
    },
  ];
}

export default function App() {
  const [healthResponse, setHealthResponse] = useState<HealthApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadHealth() {
      setLoading(true);
      setError(null);

      try {
        const payload = await fetchHealth(controller.signal);
        setHealthResponse(payload);
      } catch (fetchError) {
        if (fetchError instanceof Error && fetchError.name === "AbortError") {
          return;
        }

        setError(fetchError instanceof Error ? fetchError.message : "Backend health check failed.");
      } finally {
        setLoading(false);
      }
    }

    void loadHealth();

    return () => controller.abort();
  }, []);

  const backendHealth = healthResponse?.data?.services.backend;
  const statusTone = healthResponse?.data?.status ?? "unavailable";
  const serviceEntries = buildServiceEntries(healthResponse?.data?.services);

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">Step5 / Local HF Provider</p>
        <h1>AI Desktop Assistant</h1>
        <p className="hero-copy">
          The desktop shell still reads runtime state from `/api/v1/health`, and that payload now
          includes the configured local Hugging Face provider alongside backend service health.
        </p>
      </section>

      <section className="health-grid" aria-label="Backend health status">
        <article className="health-panel">
          <div className="section-heading">
            <div>
              <p className="section-kicker">Live Backend Status</p>
              <h2>Health Endpoint</h2>
            </div>
            <span className={`status-pill status-pill--${statusTone}`}>
              {loading ? "Checking" : error ? "Unavailable" : formatStatusLabel(statusTone)}
            </span>
          </div>

          {loading ? (
            <p className="status-copy">Loading backend health from `127.0.0.1:8000`...</p>
          ) : null}

          {error ? (
            <div className="status-stack" role="alert">
              <p className="status-copy">Backend request failed.</p>
              <p className="status-meta">{error}</p>
            </div>
          ) : null}

          {!loading && !error && healthResponse?.data ? (
            <div className="status-stack">
              <p className="status-copy">
                Backend and local provider status are reported through one health response.
              </p>
              <dl className="status-details">
                <div>
                  <dt>Overall Status</dt>
                  <dd>{formatStatusLabel(healthResponse.data.status)}</dd>
                </div>
                <div>
                  <dt>Version</dt>
                  <dd>{healthResponse.data.version}</dd>
                </div>
                <div>
                  <dt>Checked At</dt>
                  <dd>{formatTimestamp(healthResponse.data.timestamp)}</dd>
                </div>
                <div>
                  <dt>Request ID</dt>
                  <dd>{healthResponse.request_id}</dd>
                </div>
              </dl>
              <div className="service-grid" aria-label="Service health breakdown">
                {serviceEntries.map((service) => (
                  <ServiceCard
                    key={service.key}
                    label={service.label}
                    fallbackProvider={service.fallbackProvider}
                    health={service.health}
                  />
                ))}
              </div>
              {backendHealth?.message ? <p className="status-meta">{backendHealth.message}</p> : null}
            </div>
          ) : null}
        </article>

        <section className="card-grid" aria-label="Project status">
          {shellCards.map((card) => (
            <article key={card.title} className="status-card">
              <h2>{card.title}</h2>
              <p>{card.description}</p>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}

type ServiceCardProps = {
  label: string;
  fallbackProvider: string;
  health: ProviderHealth | undefined;
};

function ServiceCard({ label, fallbackProvider, health }: ServiceCardProps) {
  const status = health?.status ?? "unavailable";

  return (
    <article className="service-card">
      <div className="service-card__header">
        <div>
          <p className="service-label">{label}</p>
          <h3>{health?.provider ?? fallbackProvider}</h3>
        </div>
        <span className={`status-pill status-pill--${status}`}>{formatStatusLabel(status)}</span>
      </div>

      <dl className="service-details">
        <div>
          <dt>Available</dt>
          <dd>{health?.available ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Latency</dt>
          <dd>{formatLatency(health?.latency_ms)}</dd>
        </div>
      </dl>

      <p className="status-meta">{health?.message ?? "No service status was returned."}</p>
    </article>
  );
}

