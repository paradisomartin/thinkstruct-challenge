# Bruno collection

Imported OpenAPI collection, stored here so it can travel with the repository.
Use the [root README](../../README.md) for installation and Make commands.
Open this directory in Bruno rather than the former Documents location.

Only local `baseUrl` is tracked; never commit credentials. Run the full collection
in sequence after ingesting/indexing the supplied dataset. Filtered search and
pagination reuse runtime variables from the first search request.

Verified: 8 requests and 9 script tests pass. Tests live under `runtime.scripts`;
Bruno's separate declarative Assertions counter remains zero. Generated response
examples are not evidence that those responses were observed.
