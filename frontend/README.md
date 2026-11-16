# Frontend — deferred

Reserved boundary for an optional frontend. No framework or package dependencies
are initialized. Backend ingestion, search correctness, and required challenge
deliverables take priority. See D-007 and D-009 in the
[decision log](../docs/decisions/README.md). Add frontend-specific configuration only when
needed; browser-exposed environment variables must never contain backend secrets.
