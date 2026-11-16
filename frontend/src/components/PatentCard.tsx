import type { Patent } from "../explore";

export default function PatentCard({ patent, onClassification, onWeek }: {
  patent: Patent; onClassification: (prefix: string) => void; onWeek: (week: string) => void;
}) {
  return (
    <article className="card border border-base-300 bg-base-100" data-patent={patent.doc_number}>
      <div className="card-body gap-3">
        <p className="text-xs text-base-content/70">Document {patent.doc_number}</p>
        <h3 className="card-title text-lg">{patent.title || "Untitled patent"}</h3>
        <div className="flex flex-wrap gap-2">
          {patent.classification && <button className="btn btn-sm" onClick={() => onClassification(patent.classification!.slice(0, 4))}>
            {patent.classification}
          </button>}
          {patent.source_week && <button className="btn btn-sm" onClick={() => onWeek(patent.source_week!)}>
            Source week {patent.source_week}
          </button>}
        </div>
        <p className="text-sm leading-relaxed">{patent.abstract || "No abstract available."}</p>
        {patent.excerpt ? (
          <div className="rounded-box bg-base-200 p-3 text-sm">
            <p className="mb-2 font-medium">Matching evidence · {patent.excerpt.source_field}
              {patent.excerpt.source_index !== null ? ` [${patent.excerpt.source_index}]` : ""}</p>
            <blockquote className="whitespace-pre-wrap">{patent.excerpt.text}</blockquote>
          </div>
        ) : <p className="text-xs text-base-content/70">Browse / structured filters; no text-match excerpt.</p>}
        <p className="break-all text-xs text-base-content/70">
          Source: {patent.source_file} · record {patent.record_index}
          {patent.score !== null ? ` · ts_rank ${patent.score.toFixed(4)}` : " · document-number order"}
        </p>
      </div>
    </article>
  );
}
