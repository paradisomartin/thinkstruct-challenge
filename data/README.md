# Data placement

The local dataset is now in `data/raw/`: 64 JSON files and 640 records, with the same fingerprint as the original discovery in `data/patent_data_small/`. It is not distributed through Git. Obtain the Thinkstruct-provided dataset separately and put extracted `patents_ipa{DATE}.json` files in `data/raw/`.

The root `.gitignore` excludes all contents of `data/` except this README, including both dataset locations and ZIP files. Raw files remain unchanged.

Run `python3 scripts/profile_dataset.py data/raw` from the project root. For a different location, pass that directory instead. See `notes/02-build-journal.md` for the observed evidence. No download URL is supplied in the repository.

Do not assume the JSON schema is uniform; inspect it before deciding the ingestion policy.
