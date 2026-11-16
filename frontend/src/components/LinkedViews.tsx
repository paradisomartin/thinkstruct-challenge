import type { ExploreRequest, ExploreResponse } from "../explore";
import PatentCard from "./PatentCard";

export default function LinkedViews({ data, request, change }: {
  data: ExploreResponse; request: ExploreRequest; change: (patch: Partial<ExploreRequest>) => void;
}) {
  const classification = (prefix: string) => change({ classification_prefix: prefix });
  const week = (date: string) => change({ source_week_from: date, source_week_to: date });
  const maxWeek = Math.max(1, ...data.source_weeks.map((bucket) => bucket.count));
  return (
    <div className="grid gap-6 lg:grid-cols-[18rem_minmax(0,1fr)]" data-testid="linked-views">
      <aside className="space-y-6">
        <section className="card border border-base-300 bg-base-100" aria-labelledby="classification-heading">
          <div className="card-body">
            <h2 id="classification-heading" className="card-title">Classifications</h2>
            <div data-testid="classification-counts">
              {data.classification_facets.map((parent) => (
                <div key={parent.prefix}>
                  <button className="btn btn-ghost w-full justify-between" data-count={parent.count}
                    aria-pressed={request.classification_prefix === parent.prefix} onClick={() => classification(parent.prefix)}>
                    <span>{parent.prefix}</span><span>{parent.count}</span>
                  </button>
                  <ul className="ml-4">
                    {parent.children.map((child) => <li key={child.prefix}>
                      <button className="btn btn-ghost btn-sm w-full justify-between" data-count={child.count}
                        aria-pressed={request.classification_prefix === child.prefix} onClick={() => classification(child.prefix)}>
                        <span>{child.prefix}</span><span>{child.count}</span>
                      </button>
                    </li>)}
                  </ul>
                </div>
              ))}
              <p className="mt-2 text-xs" data-testid="unclassified">Unclassified: {data.unclassified_count}</p>
            </div>
          </div>
        </section>
        <section className="card border border-base-300 bg-base-100" aria-labelledby="week-heading">
          <div className="card-body">
            <h2 id="week-heading" className="card-title">Source weeks</h2>
            <p className="text-xs text-base-content/70">Weekly JSON batch dates, not verified legal filing dates. Select a week or use an inclusive date range.</p>
            <ul className="max-h-96 overflow-y-auto" data-testid="week-counts">
              {data.source_weeks.map((bucket) => <li key={bucket.source_week}>
                <button className="btn btn-ghost btn-sm block h-auto w-full py-2"
                  data-count={bucket.count} onClick={() => week(bucket.source_week)}
                  aria-pressed={request.source_week_from === bucket.source_week && request.source_week_to === bucket.source_week}>
                  <span className="flex justify-between"><span>{bucket.source_week}</span><span>{bucket.count}</span></span>
                  <span aria-hidden="true" className="mt-1 block h-1 rounded bg-neutral/30"
                    style={{ width: `${bucket.count / maxWeek * 100}%` }} />
                </button>
              </li>)}
            </ul>
            <p className="text-xs" data-testid="unknown-weeks">Unknown source week: {data.unknown_source_week_count}</p>
          </div>
        </section>
      </aside>
      <section aria-labelledby="results-heading" className="min-w-0 space-y-4">
        <h2 id="results-heading" className="text-xl font-semibold" data-total={data.total_matches}>
          {data.total_matches} patents
        </h2>
        <p className="text-sm text-base-content/70">All view counts include every filtered match, not just this page.</p>
        {data.total_matches === 0 && <p className="alert">No patents match. Remove a filter or change the search.</p>}
        {data.results.map((patent) => <PatentCard key={patent.doc_number} patent={patent} onClassification={classification} onWeek={week} />)}
        <nav className="flex flex-wrap items-center gap-3" aria-label="Result pagination">
          <button className="btn" disabled={request.offset === 0}
            onClick={() => change({ offset: Math.max(0, request.offset - request.limit) })}>Previous</button>
          <span className="text-sm">{data.total_matches ? request.offset + 1 : 0}–{Math.min(request.offset + request.limit, data.total_matches)} of {data.total_matches}</span>
          <button className="btn" disabled={request.offset + request.limit >= data.total_matches}
            onClick={() => change({ offset: request.offset + request.limit })}>Next</button>
        </nav>
      </section>
    </div>
  );
}
