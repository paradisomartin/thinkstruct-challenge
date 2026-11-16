# Bruno collection

Imported OpenAPI collection, stored here so it can travel with the repository.
After the [root quick start](../../README.md), open this directory in Bruno,
or install the optional CLI and run from the repository root:

```sh
npm install --global @usebruno/cli@4.3.0
make api-test
```

The selected environment is `ThinkStruct Challenge Env`; adjust its local
`baseUrl` if using a non-default API port. Reports go to ignored
`artifacts/bruno-report.json`, with headers and bodies omitted.

Only local `baseUrl` is tracked; never commit credentials. Run the full collection
in sequence after ingesting/indexing the supplied dataset. Filtered search and
pagination reuse runtime variables from the first search request.

Current v1 collection: 9 requests and 10 script tests passed, including linked-view
count consistency for `/api/v1/patents/explore`. Tests live under `runtime.scripts`;
Bruno's separate declarative Assertions counter remains zero. Generated response
examples are not evidence that those responses were observed.

Ninja owns the schema at `/api/openapi.json`; `make openapi` exports it to
`artifacts/openapi.json`. For schema updates, import that file into a separate
collection and merge changes without overwriting curated tests.
See [Bruno's import guide](https://docs.usebruno.com/open-api/importOAS).
GUI import was not independently tested.
