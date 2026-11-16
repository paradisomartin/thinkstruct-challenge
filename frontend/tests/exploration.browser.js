// Run inside a real browser with agent-browser; the Python runner supplies the page.
(async () => {
  const passed = [];
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const frame = () => new Promise(requestAnimationFrame);
  const until = async (predicate) => {
    await frame();
    const deadline = performance.now() + 15000;
    while (!predicate()) {
      if (performance.now() > deadline) throw new Error("Timed out waiting for UI");
      await frame();
    }
  };
  const button = (text) => [...document.querySelectorAll("button")].find((node) => node.textContent.trim() === text);
  const remove = (label) => document.querySelector(`button[aria-label="${label}"]`);
  const ready = async (total) => {
    await until(() => document.querySelector("[data-total]")?.dataset.total === String(total));
    await frame(); await frame(); await frame();
  };
  const fill = async (name, value) => {
    const input = document.querySelector(`input[name="${name}"]`);
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(input, value);
    input.dispatchEvent(new Event("input", { bubbles: true }));
    await frame();
  };
  const submit = async (query, total) => {
    await fill("query", query);
    document.querySelector("form").requestSubmit();
    await ready(total);
  };
  const coherent = (total) => {
    assert(Number(document.querySelector("[data-total]").dataset.total) === total, "List total");
    const parents = [...document.querySelectorAll('[data-testid="classification-counts"] > div > button')];
    const sum = (nodes) => nodes.reduce((n, node) => n + Number(node.dataset.count), 0);
    const unknown = (id) => Number(document.querySelector(`[data-testid="${id}"]`).textContent.split(":")[1]);
    assert(sum(parents) + unknown("unclassified") === total, "Classification total disagrees");
    for (const parent of parents) {
      assert(sum([...parent.parentElement.querySelectorAll("li button")]) === Number(parent.dataset.count), "Children disagree");
    }
    assert(sum([...document.querySelectorAll('[data-testid="week-counts"] button')]) + unknown("unknown-weeks") === total, "Timeline disagrees");
  };
  const clear = async () => { button("Clear all").click(); await ready(640); };
  await ready(640); coherent(640);
  assert(document.querySelectorAll("[data-patent]").length === 20, "Initial page size");
  const first = document.querySelector("[data-patent]").dataset.patent;
  button("Next").click(); await until(() => document.querySelector("[data-patent]")?.dataset.patent !== first);
  await ready(640); coherent(640);
  button("Previous").click(); await ready(640);
  assert(document.querySelector("[data-patent]").dataset.patent === first, "Stable pagination");
  passed.push("Live browse, full-set linked counts and pagination");

  await submit("wheel spoke", 114); coherent(114);
  assert(document.querySelector("blockquote")?.textContent.length > 0, "Original evidence missing");
  const facet = (prefix) => [...document.querySelectorAll('[data-testid="classification-counts"] button')]
    .find((node) => node.querySelector("span").textContent === prefix);
  facet("B60").click(); await ready(114);
  facet("B60B").click();
  await until(() => !!remove("Remove Classification: B60B") && !!document.querySelector("[data-total]"));
  const classifiedTotal = Number(document.querySelector("[data-total]").dataset.total);
  coherent(classifiedTotal);
  document.querySelector('[aria-controls="advanced-filters"]').click();
  await fill("title_keywords", "wheel");
  document.querySelector("form").requestSubmit(); await ready(55); coherent(55);
  const nextQueryTotal = await fetch("/api/v1/patents/explore?query=wheel&classification_prefix=B60B&title_keywords=wheel")
    .then((r) => r.json()).then((body) => body.total_matches);
  await submit("wheel", nextQueryTotal);
  assert(remove("Remove Classification: B60B") && remove("Remove Title keyword: wheel"), "New query lost filters");
  const dateButton = document.querySelector('[data-testid="week-counts"] button');
  const date = dateButton.querySelector("span > span").textContent;
  const datedTotal = Number(dateButton.dataset.count);
  dateButton.click(); await ready(datedTotal); coherent(datedTotal);
  remove("Remove Classification: B60B").click();
  await until(() => !remove("Remove Classification: B60B") && !!document.querySelector("[data-total]"));
  assert(remove(`Remove Source week from: ${date}`) && remove("Remove Title keyword: wheel"), "Out-of-order removal lost other filters");
  remove(`Remove Source week to: ${date}`).click();
  await until(() => !!document.querySelector("[data-total]"));
  assert(remove(`Remove Source week from: ${date}`), "Date bounds not independently removable");
  passed.push("Text evidence, hierarchy drill-down, date selection, retained query filters and independent removal");

  await clear();
  // Selecting from a result card filters the other views too.
  document.querySelector("[data-patent] button").click();
  await until(() => !!remove("Remove Classification: B60B") && !!document.querySelector("[data-total]"));
  coherent(298);
  await clear();
  await submit("zzthinkstructnomatchzz", 0); coherent(0);
  assert(document.body.textContent.includes("No patents match"), "Empty state missing");
  await fill("query", "the and of");
  document.querySelector("form").requestSubmit();
  await until(() => !!document.querySelector('[role="alert"]'));
  assert(!document.querySelector('[data-testid="linked-views"]'), "Error left stale views");
  passed.push("Result-card filtering, empty state and real 422 validation");
  await clear();

  // Deterministic out-of-order network completion, deliberately ignoring abort.
  const realFetch = window.fetch;
  const pending = [];
  window.fetch = (url) => new Promise((resolve, reject) => pending.push({ url, resolve, reject }));
  const searchPending = async (query) => {
    await fill("query", query); document.querySelector("form").requestSubmit();
    await frame();
    assert(!document.querySelector('[data-testid="linked-views"]'), "Loading shows stale views");
  };
  try {
    await searchPending("old");
    await searchPending("new");
    assert(pending.length === 2, "Expected two controlled requests");
    const fixture = await realFetch("/api/v1/patents/explore?query=wheel&limit=20").then((r) => r.json());
    pending[1].resolve(new Response(JSON.stringify(fixture)));
    await ready(fixture.total_matches);
    const obsolete = { ...fixture, total_matches: 999999 };
    pending[0].resolve(new Response(JSON.stringify(obsolete)));
    await frame(); await frame();
    coherent(fixture.total_matches);
    assert(remove("Remove Query: new"), "Older success replaced current filters");
    await searchPending("old-error");
    await searchPending("latest");
    pending[3].resolve(new Response(JSON.stringify(fixture))); await ready(fixture.total_matches);
    pending[2].reject(new Error("Obsolete network failure")); await frame(); await frame();
    assert(!document.querySelector('[role="alert"]'), "Older error replaced newer success");
    coherent(fixture.total_matches);
    await searchPending("zzthinkstructnomatchzz");
    pending[4].reject(new TypeError("Network unavailable"));
    await until(() => !!document.querySelector('[role="alert"]'));
    assert(!document.querySelector('[data-testid="linked-views"]'), "Network error shows old views");
    window.fetch = realFetch;
    button("Retry").click();
    await ready(0);
  } finally { window.fetch = realFetch; }
  passed.push("Loading isolation, stale success/error rejection even without abort, network error and retry");

  await clear();
  await fill("source_week_from", "2024-02-22");
  await fill("source_week_to", "2024-02-15");
  document.querySelector("form").requestSubmit();
  await until(() => !!document.querySelector('[role="alert"]'));
  assert(!document.querySelector('[data-testid="linked-views"]'), "Invalid dates show stale results");
  await clear();
  passed.push("Reversed date range validation");

  // Warm local production bundle, filter event → committed views → paint opportunity.
  const samples = [];
  for (let i = 0; i < 23; i++) {
    performance.clearMeasures("explore-update");
    facet("B60B").click(); await ready(298); coherent(298);
    const measurement = performance.getEntriesByName("explore-update").at(-1);
    assert(measurement?.detail.total === 298, "Missing filter render measurement");
    if (i >= 3) samples.push(measurement.duration);
    remove("Remove Classification: B60B").click(); await ready(640);
  }
  const sorted = [...samples].sort((a, b) => a - b);
  return {
    passed, browser: navigator.userAgent, dataset_patents: 640, source_weeks: 64,
    measurement: "B60B selection from browse: event handler to second animation frame after linked-view commit",
    warmups: 3, repetitions: 20, samples_ms: samples,
    median_ms: (sorted[9] + sorted[10]) / 2, p95_ms: sorted[18],
    min_ms: sorted[0], max_ms: sorted.at(-1),
  };
})()
