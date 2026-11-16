import { initialRequest, type ExploreRequest, type ExploreResponse } from "../explore";
import PatentCard from "./PatentCard";

export default function LinkedViews({ data, request, change }: {
  data: ExploreResponse; request: ExploreRequest; change: (patch: Partial<ExploreRequest>) => void;
}) {
  const classification = (prefix: string) => change({ classification_prefix: prefix });
  const week = (date: string) => change({ source_week_from: date, source_week_to: date });
  const maxWeek = Math.max(1, ...data.source_weeks.map((bucket) => bucket.count));
  const page = Math.floor(request.offset / request.limit) + 1;
  const pageCount = Math.ceil(data.total_matches / request.limit);
  const firstPage = Math.max(1, Math.min(page - 1, pageCount - 2));
  const pages = Array.from({ length: Math.min(3, pageCount) }, (_, index) => firstPage + index);
  return (
    <div className="grid gap-6 lg:grid-cols-[17.5rem_minmax(0,1fr)]" data-testid="linked-views">
      <aside className="space-y-4 text-base-content">
        <section className="card border border-base-300 bg-base-100" aria-labelledby="classification-heading">
          <div className="card-body gap-3 p-5">
            <div>
              <h2 id="classification-heading" className="card-title text-base">Classifications</h2>
              <p className="mt-1 text-xs text-muted">Matching patents by class</p>
            </div>
            <div data-testid="classification-counts">
              {data.classification_facets.map((parent) => (
                <div key={parent.prefix}>
                  <button className="btn btn-ghost btn-sm w-full justify-between px-2 text-[13px] aria-pressed:bg-selected aria-pressed:text-primary" data-count={parent.count}
                    aria-pressed={request.classification_prefix === parent.prefix} onClick={() => classification(parent.prefix)}>
                    <span>{parent.prefix}</span><span>{parent.count}</span>
                  </button>
                  <ul className="ml-2 border-l border-base-300 pl-2">
                    {parent.children.map((child) => <li key={child.prefix}>
                      <button className="btn btn-ghost btn-sm w-full justify-between px-2 text-[13px] font-medium aria-pressed:bg-selected aria-pressed:text-primary" data-count={child.count}
                        aria-pressed={request.classification_prefix === child.prefix} onClick={() => classification(child.prefix)}>
                        <span>{child.prefix}</span><span>{child.count}</span>
                      </button>
                    </li>)}
                  </ul>
                </div>
              ))}
              <p className="mt-4 border-t border-base-300 pt-3 text-xs text-muted" data-testid="unclassified">Unclassified: {data.unclassified_count}</p>
            </div>
          </div>
        </section>
        <section className="card border border-base-300 bg-base-100" aria-labelledby="week-heading">
          <div className="card-body gap-3 p-5">
            <h2 id="week-heading" className="card-title text-base">Source weeks</h2>
            <p className="text-xs leading-5 text-muted">Source file dates, not verified legal filing dates.</p>
            <p className="text-xs text-muted">Select a week or use a date range.</p>
            <ul className="max-h-32 overflow-y-auto" data-testid="week-counts">
              {data.source_weeks.map((bucket) => <li key={bucket.source_week}>
                <button className="btn btn-ghost btn-sm block h-auto w-full px-0 py-2 text-[13px] font-medium aria-pressed:bg-selected aria-pressed:text-primary"
                  data-count={bucket.count} onClick={() => week(bucket.source_week)}
                  aria-pressed={request.source_week_from === bucket.source_week && request.source_week_to === bucket.source_week}>
                  <span className="flex justify-between"><span>{bucket.source_week}</span><span>{bucket.count}</span></span>
                  <span aria-hidden="true" className="mt-1 block h-[3px] rounded bg-distribution"
                    style={{ width: `${bucket.count / maxWeek * 100}%` }} />
                </button>
              </li>)}
            </ul>
            <p className="text-xs text-muted" data-testid="unknown-weeks">Unknown source week: {data.unknown_source_week_count}</p>
          </div>
        </section>
      </aside>
      <section aria-labelledby="results-heading" className="min-w-0 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 id="results-heading" className="text-[22px] leading-7 font-semibold" data-total={data.total_matches}>
            {data.total_matches} patents
          </h2>
          <span className="badge h-7 border-base-300 bg-base-100 text-xs text-muted">{request.query ? "Text search" : "Browse mode"}</span>
          <p className="w-full text-xs leading-5">All counts reflect every filtered match, not just this page.</p>
        </div>
        {data.total_matches === 0 && <div className="card border border-base-300 bg-base-100 text-base-content">
          <div className="card-body gap-4 p-6">
            <h3 className="card-title text-xl">No patents found</h3>
            <p className="text-sm text-muted">No patents match. Try fewer search terms or clear your filters. All terms and filters combine with AND.</p>
            <div className="card-actions items-center gap-4">
              <button className="btn" onClick={() => change({ ...initialRequest, query: request.query })}>Clear filters</button>
              <span className="text-xs text-muted">Your search terms stay in the search field.</span>
            </div>
          </div>
        </div>}
        {data.results.map((patent) => <PatentCard key={patent.doc_number} patent={patent} onClassification={classification} onWeek={week} />)}
        <nav className="flex flex-wrap items-center gap-1 pt-2" aria-label="Result pagination">
          <span className="mr-auto text-xs">{data.total_matches ? request.offset + 1 : 0}–{Math.min(request.offset + request.limit, data.total_matches)} of {data.total_matches}</span>
          <button className="btn btn-sm h-9 border-base-300 bg-base-100 text-base-content" disabled={request.offset === 0}
            onClick={() => change({ offset: Math.max(0, request.offset - request.limit) })}>Previous</button>
          {pages.map((number) => <button key={number}
            className="btn btn-sm h-9 min-w-9 border-base-300 bg-base-100 text-base-content aria-[current=page]:border-primary aria-[current=page]:bg-primary aria-[current=page]:text-primary-content"
            aria-label={`Page ${number}`} aria-current={number === page ? "page" : undefined}
            onClick={() => change({ offset: (number - 1) * request.limit })}>{number}</button>)}
          {pages.at(-1)! < pageCount && <span className="px-1" aria-hidden="true">…</span>}
          <button className="btn btn-sm h-9 border-base-300 bg-base-100 text-base-content" disabled={request.offset + request.limit >= data.total_matches}
            onClick={() => change({ offset: request.offset + request.limit })}>Next</button>
        </nav>
      </section>
    </div>
  );
}
