export default function App() {
  return (
    <main className="shell">
      <header>
        <p className="eyebrow">Thinkstruct / Patent search</p>
        <h1>Explore patents with source evidence.</h1>
        <p>
          The React workspace is ready. Linked results, classifications and a
          weekly timeline are the next implementation step.
        </p>
      </header>
      <section aria-labelledby="workspace-status">
        <h2 id="workspace-status">Workspace initialized</h2>
        <p>
          This is a setup screen, not the completed Part 3 search interface.
          Django remains the search backend.
        </p>
        <a href="/api/docs">Open the backend API documentation</a>
      </section>
    </main>
  );
}
