import json

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from patents.services.ingestion import IngestionError, ingest_directory


class Command(BaseCommand):
    help = "Validate and ingest patent JSON files atomically; never overwrite conflicts."

    def add_arguments(self, parser):
        parser.add_argument("directory")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            result = ingest_directory(options["directory"], dry_run=options["dry_run"])
        except (IngestionError, IntegrityError) as exc:
            raise CommandError(f"Ingestion aborted; no changes committed: {exc}") from exc
        self.stdout.write(json.dumps(result, sort_keys=True))
