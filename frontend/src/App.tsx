import SearchPanel from "./components/SearchPanel";
import LinkedViews from "./components/LinkedViews";
import useExplore from "./useExplore";
import { initialRequest, type ExploreRequest } from "./explore";

export default function App() {
  const exploration = useExplore();
  const { request, status, data, error, run } = exploration;
  const change = (patch: Partial<ExploreRequest>) => run({ ...request, offset: 0, ...patch });
  const labels: Record<string, string> = {
    query: "Query", classification_prefix: "Classification", title_keywords: "Title keyword",
    abstract_keywords: "Abstract keyword", title_exact: "Exact title",
    source_week_from: "Source week from", source_week_to: "Source week to",
  };
  return (
    <div className="min-h-screen bg-base-200 text-base-content">
      <a className="btn btn-primary sr-only focus:not-sr-only focus:absolute focus:z-10 focus:m-3" href="#main">
        Skip to content
      </a>
      <header className="border-b border-base-300 bg-base-100">
        <nav className="navbar mx-auto max-w-6xl flex-wrap gap-3 px-4 sm:px-6" aria-label="Main navigation">
          <a className="flex items-center gap-3 rounded-sm focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary" href="./" aria-label="Thinkstruct Patent Search home">
            <span className="flex size-10 items-center justify-center rounded-box bg-neutral font-bold text-neutral-content" aria-hidden="true">
              TS
            </span>
            <span>
              <span className="block font-semibold tracking-tight">Thinkstruct</span>
              <span className="block text-xs text-base-content/70">Patent Search</span>
            </span>
          </a>
          <span className="badge badge-outline ml-auto">Patent exploration</span>
        </nav>
      </header>

      <main id="main" tabIndex={-1} className="mx-auto max-w-6xl space-y-8 px-4 py-8 sm:px-6 sm:py-12">
        <div className="max-w-2xl space-y-3">
          <p className="text-sm font-medium">Patent research workspace</p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Find the ideas behind the invention.
          </h1>
          <p className="text-base-content/70">
            Explore vehicle patents through text, classifications and source evidence.
          </p>
        </div>

        <SearchPanel request={request} onSearch={run} />
        <section aria-label="Active filters" className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium">Active filters</span>
          {Object.entries(labels).flatMap(([key, label]) => {
            const field = key as keyof typeof labels & keyof ExploreRequest;
            const value = request[field];
            const values = Array.isArray(value) ? value : value ? [String(value)] : [];
            return values.map((term) => (
              <button key={`${key}:${term}`} className="btn btn-sm"
                aria-label={`Remove ${label}: ${term}`}
                onClick={() => change({ [key]: Array.isArray(value) ? value.filter((item) => item !== term) : "" })}>
                {label}: {term} ×
              </button>
            ));
          })}
          <button className="btn btn-ghost btn-sm" onClick={() => run(initialRequest)}>Clear all</button>
        </section>
        <div aria-live="polite" role="status">
          {status === "loading" ? <p><span className="loading loading-spinner loading-sm" aria-hidden="true" /> Updating all views…</p>
            : status === "ready" ? `${data!.total_matches} patents loaded.` : "Search failed."}
        </div>
        {status === "error" && <div role="alert" className="alert alert-error">
          <p>{error}</p><button className="btn btn-sm" onClick={() => run(request)}>Retry</button>
        </div>}
        {status === "ready" && data && <LinkedViews data={data} request={request} change={change} />}

        <footer className="border-t border-base-300 pt-5 text-sm text-base-content/70">
          Thinkstruct Coding Challenge · Linked patent exploration
        </footer>
      </main>
    </div>
  );
}
