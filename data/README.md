# Data placement

Obtain the Thinkstruct-provided dataset separately and put extracted
`patents_ipa{DATE}.json` files in `data/raw/`. It is not distributed through Git.
The measured sample contains 64 JSON files and 640 records; its fingerprint is
recorded in [dataset discovery](../docs/journal/01-dataset-discovery.md).

The root `.gitignore` excludes all contents of `data/` except this README,
including ZIP files. Ingestion preserves the source files.

The [root README](../README.md) owns profiling/ingestion commands. For a different dataset location, pass that directory to the profiler. See the [journal](../docs/journal/README.md) for the observed evidence. No download URL is supplied in the repository.

Do not assume the JSON schema is uniform; inspect it before deciding the ingestion policy.
