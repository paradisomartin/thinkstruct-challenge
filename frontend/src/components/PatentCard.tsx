type PatentCardProps = {
  title: string;
  classification: string;
  excerpt: string;
};

export default function PatentCard({ title, classification, excerpt }: PatentCardProps) {
  return (
    <article className="card border border-base-300 bg-base-100 shadow-sm">
      <div className="card-body gap-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="badge badge-primary badge-soft">{classification}</span>
          <span className="badge badge-ghost">Illustrative patent</span>
        </div>
        <h3 className="card-title text-lg">{title}</h3>
        <p className="text-sm leading-relaxed text-base-content/70">{excerpt}</p>
        <div className="rounded-box bg-base-200 p-3 text-xs text-base-content/70">
          Source evidence will appear here after API integration.
        </div>
      </div>
    </article>
  );
}
