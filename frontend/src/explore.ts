export type ExploreRequest = {
  query: string;
  classification_prefix: string;
  title_keywords: string[];
  abstract_keywords: string[];
  title_exact: string;
  source_week_from: string;
  source_week_to: string;
  limit: number;
  offset: number;
};

export const initialRequest: ExploreRequest = {
  query: "", classification_prefix: "", title_keywords: [], abstract_keywords: [],
  title_exact: "", source_week_from: "", source_week_to: "", limit: 20, offset: 0,
};

export type Patent = {
  doc_number: string;
  title: string | null;
  abstract: string | null;
  classification: string | null;
  source_file: string;
  record_index: number;
  source_week: string | null;
  score: number | null;
  ranking_method: "ts_rank" | "doc_number";
  excerpt: { text: string; source_field: string; source_index: number | null } | null;
};

export type ExploreResponse = {
  results: Patent[];
  total_matches: number;
  effective_request: ExploreRequest;
  classification_facets: { prefix: string; count: number; children: { prefix: string; count: number }[] }[];
  unclassified_count: number;
  source_weeks: { source_week: string; count: number }[];
  unknown_source_week_count: number;
};

export function requestParams(request: ExploreRequest) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(request)) {
    if (Array.isArray(value)) value.forEach((term) => params.append(key, term));
    else if (value !== "") params.set(key, String(value));
  }
  return params;
}

export async function fetchExplore(request: ExploreRequest, signal: AbortSignal): Promise<ExploreResponse> {
  const response = await fetch(`/api/v1/patents/explore?${requestParams(request)}`, { signal });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    throw new Error(typeof detail === "string" ? detail
      : Array.isArray(detail) ? detail.map((item) => item.msg).join("; ")
      : `Search unavailable (HTTP ${response.status}). Please retry.`);
  }
  return response.json();
}
