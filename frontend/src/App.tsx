import SearchPanel from "./components/SearchPanel";
import ResultsPreview from "./components/ResultsPreview";

export default function App() {
  return (
    <div className="min-h-screen bg-base-200 text-base-content">
      <a className="btn btn-primary sr-only focus:not-sr-only focus:absolute focus:z-10 focus:m-3" href="#main">
        Skip to content
      </a>
      <header className="border-b border-base-300 bg-base-100">
        <nav className="navbar mx-auto max-w-6xl flex-wrap gap-3 px-4 sm:px-6" aria-label="Main navigation">
          <a className="flex items-center gap-3 rounded-sm focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary" href="./" aria-label="Thinkstruct Patent Search home">
            <span className="flex size-10 items-center justify-center rounded-box bg-primary font-bold text-primary-content" aria-hidden="true">
              TS
            </span>
            <span>
              <span className="block font-semibold tracking-tight">Thinkstruct</span>
              <span className="block text-xs text-base-content/70">Patent Search</span>
            </span>
          </a>
          <span className="badge badge-outline ml-auto">UI preview</span>
        </nav>
      </header>

      <main id="main" tabIndex={-1} className="mx-auto max-w-6xl space-y-8 px-4 py-8 sm:px-6 sm:py-12">
        <div className="max-w-2xl space-y-3">
          <p className="text-sm font-medium text-primary">Patent research workspace</p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Find the ideas behind the invention.
          </h1>
          <p className="text-base-content/70">
            Explore vehicle patents through text, classifications and source evidence.
          </p>
        </div>

        <div role="note" className="alert alert-soft">
          <p>
            <span className="font-semibold">Design preview.</span> Cards are illustrative,
            not search results. Search and API integration are not connected yet.
          </p>
        </div>

        <SearchPanel />
        <ResultsPreview />

        <footer className="border-t border-base-300 pt-5 text-sm text-base-content/70">
          Thinkstruct Coding Challenge · Interface foundation
        </footer>
      </main>
    </div>
  );
}
