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
    <div className="min-h-screen bg-workspace bg-workspace-gradient text-workspace-content">
      <a className="btn btn-primary sr-only focus:not-sr-only focus:absolute focus:z-10 focus:m-3" href="#main">
        Skip to content
      </a>
      <header className="border-b border-base-300 bg-base-100 text-base-content">
        <nav className="navbar mx-auto min-h-16 max-w-[1440px] flex-wrap gap-3 px-4 sm:px-6 lg:px-12" aria-label="Main navigation">
          <a className="flex items-center gap-3 rounded-sm focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary" href="./" aria-label="Thinkstruct Patent Search home">
            <span className="flex size-8 items-center justify-center rounded-field bg-neutral text-sm font-bold text-neutral-content" aria-hidden="true">
              TS
            </span>
            <span>
              <span className="block text-[17px] font-bold tracking-tight">Thinkstruct</span>
              <span className="block text-xs text-muted">Patent Search</span>
            </span>
          </a>
          <span className="badge ml-auto h-10 border-base-300 bg-base-100 px-4 text-xs sm:text-sm">Patent exploration</span>
        </nav>
      </header>

      <main id="main" tabIndex={-1} className="mx-auto max-w-[1440px] space-y-6 px-4 py-6 sm:px-6 lg:px-12">
        <div className="space-y-1">
          <h1 className="text-2xl leading-tight font-semibold tracking-tight sm:text-[28px]">
            Find the ideas behind the invention.
          </h1>
          <p className="text-sm leading-5">
            Explore vehicle patents through text, classifications and source evidence.
          </p>
        </div>

        <SearchPanel request={request} onSearch={run} />
        <section aria-label="Active filters" className="flex flex-wrap items-center gap-2">
          <span className="mr-1 text-xs font-semibold">Active filters</span>
          {Object.entries(labels).flatMap(([key, label]) => {
            const field = key as keyof typeof labels & keyof ExploreRequest;
            const value = request[field];
            const values = Array.isArray(value) ? value : value ? [String(value)] : [];
            return values.map((term) => (
              <button key={`${key}:${term}`} className="btn btn-sm h-auto min-h-7 max-w-full border-0 bg-selected py-1 text-xs break-words whitespace-normal text-primary"
                aria-label={`Remove ${label}: ${term}`}
                onClick={() => change({ [key]: Array.isArray(value) ? value.filter((item) => item !== term) : "" })}>
                {label}: {term} ×
              </button>
            ));
          })}
          <button className="btn btn-ghost btn-sm text-workspace-content hover:bg-workspace-content/10" onClick={() => run(initialRequest)}>Clear all</button>
        </section>
        <div aria-live="polite" role="status" className="sr-only">
          {status === "loading" ? "Updating all views…" : status === "ready" ? `${data!.total_matches} patents loaded.` : "Search failed."}
        </div>
        {status === "loading" && <div className="card border border-base-300 bg-base-100 text-base-content">
          <div className="card-body gap-3 p-6">
            <h2 className="card-title text-lg">Loading patents…</h2>
            <p className="text-sm text-muted">Updating results, classifications and source weeks.</p>
            <div aria-hidden="true" className="mt-4 space-y-3 motion-reduce:animate-none">
              <div className="skeleton h-2.5 w-44 motion-reduce:animate-none" />
              <div className="skeleton h-4 w-2/3 motion-reduce:animate-none" />
              <div className="skeleton h-2.5 w-5/6 motion-reduce:animate-none" />
            </div>
          </div>
        </div>}
        {status === "error" && <div role="alert" className="alert alert-error border border-error-content/20 p-6 sm:alert-horizontal">
          <div className="space-y-2">
            <h2 className="text-lg font-semibold">We couldn’t load patents.</h2>
            <p className="text-sm">{error}</p>
            <p className="text-sm">Your search terms and filters have been kept.</p>
          </div>
          <button className="btn ml-auto bg-base-100 text-base-content" aria-label="Retry" onClick={() => run(request)}>Try again</button>
        </div>}
        {status === "ready" && data && <LinkedViews data={data} request={request} change={change} />}

        <footer className="border-t border-workspace-content/30 pt-5 text-xs">
          Thinkstruct Coding Challenge · Linked patent exploration
        </footer>
      </main>
    </div>
  );
}
