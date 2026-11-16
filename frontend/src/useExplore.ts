import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { fetchExplore, initialRequest, type ExploreRequest, type ExploreResponse } from "./explore";

type State = {
  request: ExploreRequest;
  status: "loading" | "ready" | "error";
  data: ExploreResponse | null;
  error: string;
  id: number;
  started: number;
};

export default function useExplore() {
  const sequence = useRef(0);
  const controller = useRef<AbortController | null>(null);
  const [state, setState] = useState<State>({
    request: initialRequest, status: "loading", data: null, error: "", id: 0, started: 0,
  });

  const run = useCallback((request: ExploreRequest) => {
    const id = ++sequence.current;
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    const started = performance.now();
    // Clear all three views in the same update as the new filters.
    setState({ request, status: "loading", data: null, error: "", id, started });
    void fetchExplore(request, current.signal).then(
      (data) => {
        if (id !== sequence.current) return;
        setState({ request, status: "ready", data, error: "", id, started });
      },
      (error: unknown) => {
        if (id !== sequence.current || current.signal.aborted) return;
        setState({ request, status: "error", data: null,
          error: error instanceof Error ? error.message : "Search unavailable. Please retry.", id, started });
      },
    );
  }, []);

  useEffect(() => {
    run(initialRequest);
    return () => { ++sequence.current; controller.current?.abort(); };
  }, [run]);

  useLayoutEffect(() => {
    if (state.status !== "ready") return;
    let second = 0;
    // Second animation frame: the committed linked views had a paint opportunity.
    const first = requestAnimationFrame(() => {
      second = requestAnimationFrame(() => {
        if (state.id !== sequence.current) return;
        performance.measure("explore-update", {
          start: state.started, end: performance.now(),
          detail: { request: state.request, total: state.data!.total_matches },
        });
      });
    });
    return () => { cancelAnimationFrame(first); cancelAnimationFrame(second); };
  }, [state]);

  return { ...state, run };
}
