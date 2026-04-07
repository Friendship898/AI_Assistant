import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            status: "healthy",
            version: "0.1.0",
            timestamp: "2026-04-07T13:15:46.294600Z",
            services: {
              backend: {
                provider: "backend",
                available: true,
                status: "healthy",
                latency_ms: null,
                message: "FastAPI service is running.",
              },
              local_llm: {
                provider: "huggingface_local",
                available: true,
                status: "healthy",
                latency_ms: 12.4,
                message: "Loaded local model 'Qwen3-14B' from 'D:\\AI\\Models\\Qwen3-14B'.",
              },
            },
          },
          error: null,
          request_id: "frontend-health-test",
          timestamp: "2026-04-07T13:15:46.295593Z",
        }),
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the Step4 shell heading and local provider health state", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /AI Desktop Assistant/i })).toBeInTheDocument();
    expect(screen.getByText(/Step4 \/ Local HF Provider/i)).toBeInTheDocument();
    expect(await screen.findByText(/Backend and local provider status are reported through one health response\./i)).toBeInTheDocument();
    expect(
      screen.getByText(/Loaded local model 'Qwen3-14B' from 'D:\\AI\\Models\\Qwen3-14B'\./i),
    ).toBeInTheDocument();
    expect(screen.getByText(/frontend-health-test/i)).toBeInTheDocument();
  });
});

