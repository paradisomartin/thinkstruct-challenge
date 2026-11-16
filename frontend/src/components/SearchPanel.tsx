import { useState } from "react";

const filterFields = [
  { name: "classification", label: "Classification prefix", placeholder: "e.g. B60B" },
  { name: "titleKeywords", label: "Title keywords", placeholder: "e.g. wheel" },
  { name: "abstractKeywords", label: "Abstract keywords", placeholder: "e.g. pressure" },
  { name: "exactTitle", label: "Exact title", placeholder: "Full patent title" },
] as const;

export default function SearchPanel() {
  const [query, setQuery] = useState("");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filters, setFilters] = useState({
    classification: "",
    titleKeywords: "",
    abstractKeywords: "",
    exactTitle: "",
  });

  return (
    <section aria-labelledby="search-heading" className="card border border-base-300 bg-base-100 shadow-sm">
      <div className="card-body gap-5">
        <h2 id="search-heading" className="card-title">Search patents</h2>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="fieldset min-w-0 flex-1">
            <span className="fieldset-legend">Search terms</span>
            <input
              type="search"
              className="input w-full"
              placeholder="e.g. flexible wheel spokes"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-describedby="search-help"
            />
          </label>
          <button type="button" className="btn btn-primary sm:mb-1" disabled>
            Search
          </button>
        </div>
        <p id="search-help" className="text-sm text-base-content/70">
          Inputs are editable for this preview. Search is not available yet.
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
                    value={filters[name]}
                    onChange={(event) => setFilters({ ...filters, [name]: event.target.value })}
                  />
                </label>
              ))}
            </fieldset>
          </div>
        </div>
      </div>
    </section>
  );
}
