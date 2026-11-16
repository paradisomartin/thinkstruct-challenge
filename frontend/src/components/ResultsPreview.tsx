import { useState } from "react";
import PatentCard from "./PatentCard";

type PreviewState = "results" | "empty" | "loading";

export default function ResultsPreview() {
  const [previewState, setPreviewState] = useState<PreviewState>("results");

  return (
    <section aria-labelledby="results-heading" className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 id="results-heading" className="text-xl font-semibold">Results preview</h2>
          <p className="mt-1 text-sm text-base-content/70">Layout examples only — no live patent data.</p>
        </div>
        <label className="flex flex-wrap items-center gap-2 text-sm">
          Preview state
          <select
            className="select select-sm w-36"
            value={previewState}
            onChange={(event) => setPreviewState(event.target.value as PreviewState)}
          >
            <option value="results">Patent cards</option>
            <option value="empty">Empty</option>
            <option value="loading">Loading</option>
          </select>
        </label>
      </div>

      <div aria-live="polite" aria-atomic="true">
        {previewState === "results" && (
          <div className="grid gap-4 md:grid-cols-2">
            <PatentCard
              title="Flexible wheel assembly"
              classification="B60B"
              excerpt="Example summary: a wheel assembly with flexible spokes connecting the hub and rim."
            />
            <PatentCard
              title="Tire pressure monitoring system"
              classification="B60C"
              excerpt="Example summary: a monitoring system that presents tire pressure information to the driver."
            />
          </div>
        )}

        {previewState === "empty" && (
          <div className="card border border-dashed border-base-300 bg-base-100">
            <div className="card-body items-center py-12 text-center">
              <span className="badge badge-ghost">Empty state preview</span>
              <h3 className="card-title">No patents to display</h3>
              <p className="max-w-md text-base-content/70">
                A future search with no matches will offer guidance to broaden the terms or adjust filters.
              </p>
            </div>
          </div>
        )}

        {previewState === "loading" && (
          <div className="card border border-base-300 bg-base-100">
            <div className="card-body gap-5">
              <p className="flex items-center gap-3 text-sm">
                <span className="loading loading-spinner loading-sm text-primary motion-reduce:animate-none" aria-hidden="true" />
                Loading state preview — no request is running.
              </p>
              <div className="space-y-3" aria-hidden="true">
                <div className="skeleton h-5 w-2/3 motion-reduce:animate-none" />
                <div className="skeleton h-4 w-full motion-reduce:animate-none" />
                <div className="skeleton h-4 w-4/5 motion-reduce:animate-none" />
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
