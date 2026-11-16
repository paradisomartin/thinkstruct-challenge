import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../src/App";
import { initialRequest, type ExploreResponse } from "../src/explore";

// Small synthetic fixture, not a measurement or a copy of the supplied dataset.
function response(total = 2): ExploreResponse {
  return {
    effective_request: initialRequest,
    total_matches: total,
    results: total ? [{
      doc_number: "TEST-001", title: "Wheel assembly", abstract: "Flexible spokes",
      classification: "B60B", source_file: "patents_ipa240215.json", record_index: 0,
      source_week: "2024-02-15", score: 0.1, ranking_method: "ts_rank",
      excerpt: { text: "A flexible wheel spoke.", source_field: "claims", source_index: 0 },
    }] : [],
    classification_facets: total ? [{ prefix: "B60", count: total, children: [{ prefix: "B60B", count: total }] }] : [],
    source_weeks: total ? [{ source_week: "2024-02-15", count: total }] : [],
    unclassified_count: 0, unknown_source_week_count: 0,
  };
}

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const loaded = (total: number) => screen.findByRole("heading", { name: `${total} patents` });
function search(query: string) {
  fireEvent.change(screen.getByRole("searchbox"), { target: { value: query } });
  fireEvent.click(screen.getByRole("button", { name: "Search" }));
}

beforeEach(() => {
  // jsdom has no paint pipeline. Real render timings remain in the browser suite.
  vi.stubGlobal("requestAnimationFrame", vi.fn(() => 0));
  vi.stubGlobal("cancelAnimationFrame", vi.fn());
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("linked exploration workflow", () => {
  it("links classifications and weeks, preserves filters on search, and removes them independently", async () => {
    const fetchMock = vi.fn(async (_url: string, _init?: RequestInit) => json(response()));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await loaded(2);
    expect(screen.getByText("A flexible wheel spoke.")).toBeTruthy();

    fireEvent.click(within(screen.getByTestId("classification-counts")).getByRole("button", { name: /^B60B\s*2$/ }));
    await loaded(2);
    fireEvent.click(within(screen.getByTestId("week-counts")).getByRole("button", { name: /^2024-02-15\s*2$/ }));
    await loaded(2);
    search("wheel spoke");
    await loaded(2);

    const params = () => new URL(String(fetchMock.mock.calls.at(-1)![0]), "http://localhost").searchParams;
    expect(params().get("query")).toBe("wheel spoke");
    expect(params().get("classification_prefix")).toBe("B60B");
    expect(params().get("source_week_from")).toBe("2024-02-15");
    expect(params().get("source_week_to")).toBe("2024-02-15");

    fireEvent.click(screen.getByRole("button", { name: "Remove Classification: B60B" }));
    await loaded(2);
    expect(params().has("classification_prefix")).toBe(false);
    expect(params().get("source_week_from")).toBe("2024-02-15");
    expect(params().get("query")).toBe("wheel spoke");
  });

  it("shows empty results, an API error and a successful retry without retaining old views", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json(response()))
      .mockResolvedValueOnce(json(response(0)))
      .mockResolvedValueOnce(json({ detail: "Search temporarily unavailable" }, 503))
      .mockResolvedValueOnce(json(response(1)));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await loaded(2);
    search("absent");
    await loaded(0);
    expect(screen.getByText(/No patents match/)).toBeTruthy();
    search("wheel");
    expect((await screen.findByRole("alert")).textContent).toContain("Search temporarily unavailable");
    expect(screen.queryByTestId("linked-views")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    await loaded(1);
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it.each(["success", "error"])("rejects a stale %s even when fetch ignores cancellation", async (outcome) => {
    let resolveOld!: (value: Response) => void;
    let rejectOld!: (reason: Error) => void;
    let resolveNew!: (value: Response) => void;
    const old = new Promise<Response>((resolve, reject) => { resolveOld = resolve; rejectOld = reject; });
    const latest = new Promise<Response>((resolve) => { resolveNew = resolve; });
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json(response()))
      .mockReturnValueOnce(old)
      .mockReturnValueOnce(latest);
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await loaded(2);
    search("old");
    expect(screen.queryByTestId("linked-views")).toBeNull();
    expect(screen.getByRole("status").textContent).toContain("Updating all views");
    search("latest");
    expect((fetchMock.mock.calls[1][1] as RequestInit).signal?.aborted).toBe(true);
    await act(async () => { resolveNew(json(response(1))); });
    await loaded(1);
    await act(async () => {
      if (outcome === "success") resolveOld(json(response(99)));
      else rejectOld(new Error("Obsolete failure"));
    });
    await waitFor(() => expect(screen.getByRole("heading", { name: "1 patents" })).toBeTruthy());
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByRole("heading", { name: "99 patents" })).toBeNull();
    expect(screen.getByRole("button", { name: "Remove Query: latest" })).toBeTruthy();
  });
});
