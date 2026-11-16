# Container ingestion PoC · 2026-11-16

- Selected on-demand container ingestion as the narrow Part 2 PoC, following
  user approval. Reused Part 1 commands; added only a Compose override to run
  image code without the development bind mount, on port 8001.
- Verified a fresh `thinkstruct-poc_postgres_data` volume, migrations, ingestion,
  explicit indexing and reingestion: 640 patents, 31,671 passages and 640 indexed;
  second import created nothing and reported 640 unchanged.
- Independent SQL counts and four HTTP search/filter cases matched expectations.
  Health/OpenAPI returned 200; all 55 automated tests passed from the image.
- Inspected mounts to confirm dataset read-only access and distinct database
  volumes. The existing port-8000 API remained healthy; its volume was not targeted.
- [Exact commands, results and limitations](../architecture/part-2-poc.md).
  This is local containerization, not an S3/ECS integration or scale benchmark.
- Next: select exactly one Part 3 enhancement with the user, then complete the
  final reproduction check and accessible Part 2/3 recording.
