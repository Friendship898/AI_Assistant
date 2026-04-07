const shellCards = [
  {
    title: "Desktop Shell",
    description: "React + Tauri v2 scaffold is ready for upcoming interaction flows.",
  },
  {
    title: "Backend Shell",
    description: "FastAPI bootstrap and module boundaries are in place for the next step.",
  },
  {
    title: "Project Discipline",
    description: "This repository is intentionally staying inside Step0 with no product APIs yet.",
  },
];

export default function App() {
  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">Step0 / Project Skeleton</p>
        <h1>AI Desktop Assistant</h1>
        <p className="hero-copy">
          The workspace is now organized for a Tauri desktop shell, a single FastAPI
          backend process, and future module-by-module delivery.
        </p>
      </section>

      <section className="card-grid" aria-label="Skeleton status">
        {shellCards.map((card) => (
          <article key={card.title} className="status-card">
            <h2>{card.title}</h2>
            <p>{card.description}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

