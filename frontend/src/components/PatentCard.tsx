import type { Patent } from "../explore";

export default function PatentCard({ patent, onClassification, onWeek }: {
  patent: Patent; onClassification: (prefix: string) => void; onWeek: (week: string) => void;
}) {
  return (
    <article className="card border border-base-300 bg-base-100 text-base-content" data-patent={patent.doc_number}>
      <div className="card-body gap-3 p-5 sm:p-6">
        <p className="text-xs text-muted">Document {patent.doc_number}</p>
        <h3 className="card-title text-xl leading-6.5 break-words">{patent.title || "Untitled patent"}</h3>
        <div className="flex flex-wrap gap-2">
          {patent.classification && <button className="btn btn-sm h-7 border-0 bg-base-200 text-xs font-medium" onClick={() => onClassification(patent.classification!.slice(0, 4))}>
            {patent.classification}
          </button>}
          {patent.source_week && <button className="btn btn-sm h-7 border-0 bg-base-200 text-xs font-medium" onClick={() => onWeek(patent.source_week!)}>
            Source week {patent.source_week}
          </button>}
        </div>
        <div className="mt-1">
          <p className="mb-1 text-[11px] font-semibold tracking-wide text-muted">ABSTRACT</p>
          <p className="text-sm leading-[21px]">{patent.abstract || "No abstract available."}</p>
        </div>
        {patent.excerpt ? (
          <div className="rounded-field bg-selected p-4 text-sm">
            <p className="mb-2 text-xs font-semibold text-primary">Text match · {patent.excerpt.source_field}
              {patent.excerpt.source_index !== null ? ` [${patent.excerpt.source_index}]` : ""}</p>
            <blockquote className="whitespace-pre-wrap">{patent.excerpt.text}</blockquote>
          </div>
        ) : <div className="flex flex-wrap gap-x-4 gap-y-1 rounded-field bg-evidence px-3 py-2 text-xs text-muted">
          <span className="font-semibold">Evidence</span>
          <p>Browse / structured filters; no text-match excerpt.</p>
        </div>}
        <p className="break-all text-xs leading-5 text-muted">
          Source: {patent.source_file} · record {patent.record_index}
          {patent.score !== null ? ` · ts_rank ${patent.score.toFixed(4)}` : " · document-number order"}
        </p>
      </div>
    </article>
  );
}
