import { useEffect, useState } from "react";
import type { ExploreRequest } from "../explore";

const filterFields = [
  { name: "classification_prefix", label: "Classification prefix", placeholder: "e.g. B60B" },
  { name: "title_keywords", label: "Title keywords", placeholder: "e.g. wheel" },
  { name: "abstract_keywords", label: "Abstract keywords", placeholder: "e.g. pressure" },
  { name: "title_exact", label: "Exact title", placeholder: "Full patent title" },
] as const;

function draftOf(request: ExploreRequest) {
  return { ...request, title_keywords: request.title_keywords.join(" "), abstract_keywords: request.abstract_keywords.join(" ") };
}

export default function SearchPanel({ request, onSearch }: {
  request: ExploreRequest; onSearch: (request: ExploreRequest) => void;
}) {
  const [draft, setDraft] = useState(() => draftOf(request));
  const [filtersOpen, setFiltersOpen] = useState(false);
  useEffect(() => setDraft(draftOf(request)), [request]);

  return (
    <section aria-labelledby="search-heading" className="space-y-2">
      <form className="card border border-base-300 bg-base-100 text-base-content" onSubmit={(event) => {
        event.preventDefault();
        const terms = (value: string) => value.trim().split(/\s+/).filter(Boolean);
        onSearch({ ...draft, query: draft.query.trim(),
          title_keywords: terms(draft.title_keywords), abstract_keywords: terms(draft.abstract_keywords), offset: 0 });
      }}>
        <div className="card-body gap-0 p-4">
        <h2 id="search-heading" className="sr-only">Search patents</h2>
        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end lg:flex-nowrap">
          <label className="fieldset min-w-0 flex-1 gap-1 p-0">
            <span className="fieldset-legend py-0 text-xs">Search terms</span>
            <input
              type="search"
              className="input h-10 w-full border-base-300 text-sm placeholder:text-muted"
              placeholder="e.g. flexible wheel spokes"
              name="query"
              value={draft.query}
              onChange={(event) => setDraft({ ...draft, query: event.target.value })}
              aria-describedby="search-help"
            />
          </label>
          <button type="submit" className="btn btn-primary h-10 sm:w-28">
            Search
          </button>
          <button
            type="button"
            className="btn h-10 border-base-300 bg-base-100 lg:w-52"
            aria-expanded={filtersOpen}
            aria-controls="advanced-filters"
            onClick={() => setFiltersOpen(!filtersOpen)}
          >
            Advanced filters
            <span aria-hidden="true">{filtersOpen ? "−" : "+"}</span>
          </button>
        </div>
          <div id="advanced-filters" hidden={!filtersOpen} className="mt-5 border-t border-base-300 pt-4">
            <fieldset className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <legend className="sr-only">Advanced search filters</legend>
              {filterFields.map(({ name, label, placeholder }) => (
                <label key={name} className="fieldset min-w-0">
                  <span className="fieldset-legend">{label}</span>
                  <input
                    type="text"
                    className="input h-10 w-full border-base-300 text-sm placeholder:text-muted"
                    placeholder={placeholder}
                    name={name}
                    value={draft[name]}
                    onChange={(event) => setDraft({ ...draft, [name]: event.target.value })}
                  />
                </label>
              ))}
              {(["source_week_from", "source_week_to"] as const).map((name) => (
                <label key={name} className="fieldset min-w-0">
                  <span className="fieldset-legend">Source week {name.endsWith("from") ? "from" : "to"}</span>
                  <input type="date" name={name} className="input h-10 w-full border-base-300 text-sm" value={draft[name]}
                    onChange={(event) => setDraft({ ...draft, [name]: event.target.value })} />
                </label>
              ))}
            </fieldset>
            <p className="mt-4 text-xs text-muted">Dates are inclusive and refer to source files, not verified legal filing dates.</p>
          </div>
        </div>
      </form>
      <p id="search-help" className="text-xs leading-5">
        All terms and filters combine with AND. Leave search empty to browse. Keywords are space-separated.
      </p>
    </section>
  );
}
