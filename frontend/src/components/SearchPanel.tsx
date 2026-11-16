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
    <section aria-labelledby="search-heading" className="card border border-base-300 bg-base-100 shadow-sm">
      <form className="card-body gap-5" onSubmit={(event) => {
        event.preventDefault();
        const terms = (value: string) => value.trim().split(/\s+/).filter(Boolean);
        onSearch({ ...draft, query: draft.query.trim(),
          title_keywords: terms(draft.title_keywords), abstract_keywords: terms(draft.abstract_keywords), offset: 0 });
      }}>
        <h2 id="search-heading" className="card-title">Search patents</h2>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="fieldset min-w-0 flex-1">
            <span className="fieldset-legend">Search terms</span>
            <input
              type="search"
              className="input w-full"
              placeholder="e.g. flexible wheel spokes"
              name="query"
              value={draft.query}
              onChange={(event) => setDraft({ ...draft, query: event.target.value })}
              aria-describedby="search-help"
            />
          </label>
          <button type="submit" className="btn sm:mb-1">
            Search
          </button>
        </div>
        <p id="search-help" className="text-sm text-base-content/70">
          All terms and filters combine with AND. Leave search empty to browse. Keywords are space-separated.
        </p>

        <div className="border-t border-base-300 pt-4">
          <button
            type="button"
            className="btn btn-ghost"
            aria-expanded={filtersOpen}
            aria-controls="advanced-filters"
            onClick={() => setFiltersOpen(!filtersOpen)}
          >
            <span aria-hidden="true">{filtersOpen ? "−" : "+"}</span>
            Advanced filters
          </button>
          <div id="advanced-filters" hidden={!filtersOpen}>
            <fieldset className="mt-4 grid gap-4 sm:grid-cols-2">
              <legend className="sr-only">Advanced search filters</legend>
              {filterFields.map(({ name, label, placeholder }) => (
                <label key={name} className="fieldset min-w-0">
                  <span className="fieldset-legend">{label}</span>
                  <input
                    type="text"
                    className="input w-full"
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
                  <input type="date" name={name} className="input w-full" value={draft[name]}
                    onChange={(event) => setDraft({ ...draft, [name]: event.target.value })} />
                </label>
              ))}
            </fieldset>
          </div>
        </div>
      </form>
    </section>
  );
}
